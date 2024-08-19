import asyncio
import json
import os
import sys
from dataclasses import dataclass
from typing import Optional

import crud
import numpy as np
import tritonclient.grpc.aio as grpcclient
from sqlalchemy.orm import Session
from tritonclient.utils import InferenceServerException

# TODO:
# - Add logging
# - Add error handling
# - Add type hints


TRITON_HTTP_SERVICE = os.getenv("TRITON_HTTP_SERVICE")
TRITON_GRPC_SERVICE = os.getenv("TRITON_GRPC_SERVICE")
TRITON_METRICS_SERVICE = os.getenv("TRITON_METRICS_SERVICE")


@dataclass
class RequestFlags:
    """RequestFlags."""

    model: str
    verbose: bool
    url: str
    stream_timeout: Optional[float]
    offset: int
    iterations: int
    streaming_mode: bool
    exclude_inputs_in_outputs: bool
    lora_name: Optional[str]


class LLMService:

    async def send_context_to_model(self, context: str, model_name: str, result_id: int, db: Session):

        if TRITON_GRPC_SERVICE is None:
            raise ValueError("Triton GRPC Service not set")

        flags = RequestFlags(
            model=model_name,
            verbose=False,
            url="host.docker.internal:8001",
            stream_timeout=None,
            offset=0,
            iterations=1,
            streaming_mode=False,
            exclude_inputs_in_outputs=False,
            lora_name=None,
        )

        # Preprocess context

        triton_client = TritonClient(flags)
        await triton_client.run_async(context, result_id, db)

        # get model_name by id

        # pre / postprocessor -> enforce json?

        # TODO: typing


class TritonClient:
    def __init__(self, flags: RequestFlags):
        self._client = grpcclient.InferenceServerClient(url=flags.url, verbose=flags.verbose)
        self._flags = flags
        self._loop = asyncio.get_event_loop()
        self._results_dict = {}

    async def async_request_iterator(self, prompts, sampling_parameters, exclude_input_in_output):
        try:
            for iter in range(self._flags.iterations):
                for i, prompt in enumerate(prompts):
                    prompt_id = self._flags.offset + (len(prompts) * iter) + i
                    self._results_dict[str(prompt_id)] = []
                    request = self.create_request(
                        prompt,
                        self._flags.streaming_mode,
                        prompt_id,
                        sampling_parameters,
                        exclude_input_in_output,
                    )
                    yield request
        except Exception as error:
            print(f"Caught an error in the request iterator: {error}")

    async def stream_infer(self, prompts, sampling_parameters, exclude_input_in_output):
        try:
            response_iterator = self._client.stream_infer(
                inputs_iterator=self.async_request_iterator(prompts, sampling_parameters, exclude_input_in_output),
                stream_timeout=self._flags.stream_timeout,
            )
            async for response in response_iterator:
                yield response
        except InferenceServerException as error:
            print(error)  # TODO: logging
            sys.exit(1)

    async def process_stream(self, prompts, sampling_parameters, exclude_input_in_output):
        self.results_dict = []
        success = True
        async for response in self.stream_infer(prompts, sampling_parameters, exclude_input_in_output):
            result, error = response
            if error:
                print(f"Encountered error while processing: {error}")  # TODO: logging
                success = False
            else:
                output = result.as_numpy("text_output")
                for i in output:
                    self._results_dict[result.get_response().id].append(i)
        return success

    async def run(self, context: str, result_id: int, db: Session):

        self._client = grpcclient.InferenceServerClient(url=self._flags.url, verbose=self._flags.verbose)
        sampling_parameters = {
            "temperature": "0.1",
            "top_p": "0.95",
            "max_tokens": "100",
        }
        exclude_input_in_output = self._flags.exclude_inputs_in_outputs
        if self._flags.lora_name is not None:
            sampling_parameters["lora_name"] = self._flags.lora_name

        prompts = [context]

        success = await self.process_stream(prompts, sampling_parameters, exclude_input_in_output)

        if success:
            crud.update_result(db, result_id, "completed", str(self._results_dict))  # TODO: Postprocessing

        else:
            print("Failed to process")
            crud.update_result(db, result_id, "failed", None)

    async def run_async(self, context: str, result_id: int, db: Session):
        await self.run(context, result_id, db)

    def create_request(
        self,
        prompt,
        stream,
        request_id,
        sampling_parameters,
        exclude_input_in_output,
        send_parameters_as_tensor=True,
    ):
        inputs = []
        prompt_data = np.array([prompt.encode("utf-8")], dtype=np.object_)
        try:
            inputs.append(grpcclient.InferInput("text_input", [1], "BYTES"))
            inputs[-1].set_data_from_numpy(prompt_data)
        except Exception as error:
            print(f"Encountered an error during request creation: {error}")

        stream_data = np.array([stream], dtype=bool)
        inputs.append(grpcclient.InferInput("stream", [1], "BOOL"))
        inputs[-1].set_data_from_numpy(stream_data)

        if send_parameters_as_tensor:
            sampling_parameters_data = np.array([json.dumps(sampling_parameters).encode("utf-8")], dtype=np.object_)
            inputs.append(grpcclient.InferInput("sampling_parameters", [1], "BYTES"))
            inputs[-1].set_data_from_numpy(sampling_parameters_data)

        inputs.append(grpcclient.InferInput("exclude_input_in_output", [1], "BOOL"))
        inputs[-1].set_data_from_numpy(np.array([exclude_input_in_output], dtype=bool))

        outputs = []
        outputs.append(grpcclient.InferRequestedOutput("text_output"))

        print(f"Sending request {request_id}...")

        return {
            "model_name": self._flags.model,
            "inputs": inputs,
            "outputs": outputs,
            "request_id": str(request_id),
            "parameters": sampling_parameters,
        }
