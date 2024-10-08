# LLM API Service

### Architecture

- `app` is a FastAPI based web service that serves the LLM API. It communicates with a Postgres DB to save contexts (prompts) and results. It forwards requests to Nvidia Triton
- `db` is a Postgres DB that stores contexts and Results
- `triton` is a Nvidia Triton server that serves the LLM Models with a vLLM Backend

Requests to Nvidia Triton are performed asynchrously. This means that results have a state: `pending` if the LLM is still processing, `completed` if it has done so successfully or `failed` if not.
The client immediately returns a `<result_id>` which can be used to query the result status and content. This allows for complex / long running requests without timeouts.

### Setup

- Install Docker and Docker Compose
- Create venv, install depenencies from `requirements.txt` for development
- make sure env variables are set correctly. You can use the existing ones (`.env.api.dev`, `.env.db.dev`). They are only meant for development.
- Run `docker-compose -f docker-compose.yml up --build` to start the service

- You need to deploy a Nvidia Triton server and upload models that are vLLM compatible

### Nvidia Triton

- The `nvidia_triton` folder contains a makefile to create a Vast.ai instance if necessary. Furthermore, it allows for simple deployment / interaction with the Triton server
- The web service currently communicates via ssh tunnels with the Triton service. This can be configured differently
- Below is an example how to deloy a Triton server on Vast.ai, if you don't have a server with suitable GPU

#### Creating a Vast.ai instance with a Nvidia Triton Server (vLLM Backend) instance

- Make sure you have set up you Vast.ai API Key. Install the `vastai` python cli tool. Make sure you have the GNU `make` utility installed to use makefiles
- `make search-instance` will list available instances
- `make create-instance INSTANCE_ID=xyz` will create a new instance. It will automatically use the Nvidia Triton Image. This may take up to 10 minutes
- `make ssh-instance CONTRACT_ID=xyz` will ssh into the instance
- `make run-tritonserver CONTRACT_ID=xyz` will start the Triton server on the instance
- `make ssh-tunnels-tritonserver CONTRACT_ID=xyz` will create ssh tunnels, such that the locally deployed web service can communicate with the Triton server
- `make deploy-models-tritonserver CONTRACT_ID=xyz` will deploy the models to the Triton server. Check the `models` folder for the required structure
- `make check-health-tritonserver` will return 1 if the Triton server is healthy
- `make check-logs-tritonserver CONTRACT_ID=xyz` will show the logs of the Triton server
- `make check-model-stats-tritonserver` will show the model stats

You can adapt vastai server specifications in the `vastai_instance_definition.yaml`

### API Request Examples

- Create a context / prompt:
  `curl -X POST "localhost:8887/contexts/" -H "Content-Type: application/json" -d '{"content": "This is context"}'`

- Get all contexts / prompts:
  `curl -X GET http://localhost:8887/contexts/`

- Get a specific context / prompt:
  `curl -X GET http://localhost:8887/contexts/<context_id>`

- Get all results:
  `curl -X GET http://localhost:8887/results/`

- Get a specific result:
  `curl -X GET http://localhost:8887/results/<result_id>`

- Get all models (fetched from Triton):
  `curl -X GET http://localhost:8887/models/`

- Send a context / promt to a specific model:
  `curl -X POST http://localhost:8887/models/send/<model_name>/<context_id>`

### Database

The database stores contexts and results. The models are handled by the Nvidia Triton Model server. Contexts can be related to the results using the <context_id>.
