SHELL = /bin/bash
CONFIG_VARS := $(shell python utils/parse_yaml.py vastai_instance_definition.yaml)
INSTANCE_ID ?=
CONTRACT_ID ?=
DATA_DIR ?=
TRAIN_DIR ?=
PRIVATE_SSH_KEY ?=
REMOTE_PATH ?= /workspace
DOCKERFILE ?= Dockerfile.vastai
IMAGE_NAME ?= habichta/vastai_pytorch
TAG ?= latest
ENV='TZ=UTC'

$(foreach var, $(CONFIG_VARS), $(eval $(var)))
$(info $(INSTANCE_ID))

.PHONY: search-instance create-instance destroy-instance transfer-data transfer-training transfer-all check-lock docker-build docker-push build-all

search-instance:
	@vastai search offers 'reliability>0.99 gpu_ram>=20 dph<=0.5'

create-instance:
	@vastai create instance $(INSTANCE_ID) \
			--disk $(DISK) \
			--image $(IMAGE) \
			--label $(LABEL) \
			$(if $(filter true,$(SSH)),--ssh) \
			$(if $(filter true,$(JUPYTER)),--jupyter) \
			$(if $(filter true,$(DIRECT)),--direct) \
			$(if $(JUPYTER_DIR),--jupyter-dir $(JUPYTER_DIR)) \
			$(if $(filter true,$(JUPYTER_LAB)),--jupyter-lab) \
			$(if $(filter true,$(LANG_UTF8)),--lang-utf8) \
			$(if $(filter true,$(PYTHON_UTF8)),--python-utf8) \
			$(if $(filter true,$(FORCE)),--force) \
			--retry $(RETRY) \
			--env $(ENV) \
			--onstart-cmd "env | grep _ >> /etc/environment; echo 'starting up'" \

show-instances:
	@vastai show instances

ssh-instance:
	@ssh $(shell vastai ssh-url $(CONTRACT_ID))

destroy-instance:
	@vastai destroy instance $(CONTRACT_ID)

ssh-tunnels-tritonserver:
	@HOST=$(shell vastai ssh-url $(CONTRACT_ID) | sed 's#ssh://root@\([0-9.]*\):.*#\1#'); \
	PORT=$(shell vastai ssh-url $(CONTRACT_ID) | sed 's/.*:\([0-9]*\)/\1/'); \
		ssh -f -p $$PORT root@$$HOST -L 8000:localhost:8000 -N; \
		ssh -f -p $$PORT root@$$HOST -L 8001:localhost:8001 -N; \
		ssh -f -p $$PORT root@$$HOST -L 8002:localhost:8002 -N

run-tritonserver:
	@ssh $(shell vastai ssh-url $(CONTRACT_ID)) "\
	export PATH=\$$PATH:/opt/tritonserver/bin; \
	if [ ! -d /opt/tritonserver/models ]; then mkdir -p /opt/tritonserver/models; fi; \
	tmux new-session -d -s tritonserver 'tritonserver --model-repository=/opt/tritonserver/models --model-control-mode=poll --repository-poll-secs=5 --log-file=/opt/tritonserver/logs.log > /opt/tritonserver/tritonserver-tmux.log 2>&1'"
	

kill-tritonserver:
	@ssh $(shell vastai ssh-url $(CONTRACT_ID)) "pkill -f tritonserver"


check-health-tritonserver:
	@curl -s -o /dev/null -w "%{http_code}" localhost:8000/v2/health/ready 2>/dev/null | grep -q "200" && echo 1 || echo 0

check-logs-tritonserver:
	@ssh $(shell vastai ssh-url $(CONTRACT_ID)) "cat /opt/tritonserver/logs.log"

deploy-tritonserver: run-tritonserver check-logs-tritonserver

deploy-models-tritonserver:
 @vastai copy ./models $(CONTRACT_ID):/opt/tritonserver/models

check-model-stats-tritonserver:
	@curl -X GET http://localhost:8000/v2/models/stats | jq
