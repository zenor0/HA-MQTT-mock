.PHONY: install run test lint format clean uninstall dev-install
VENV_PATH = .venv

# 安装依赖
install:
	python3 -m venv $(VENV_PATH)
	venv/bin/pip install -r requirements.txt

# 开发模式安装
dev-install:
	python3 -m venv $(VENV_PATH)
	$(VENV_PATH)/bin/pip install -r requirements.txt
	$(VENV_PATH)/bin/pip install -e .

# 运行程序
run:
	$(VENV_PATH)/bin/python -m ha_mqtt_mock.main

# 运行测试
test:
	$(VENV_PATH)/bin/pytest tests/

# 代码格式化
format:
	$(VENV_PATH)/bin/black src/ tests/
	$(VENV_PATH)/bin/isort src/ tests/

# 代码检查
lint:
	$(VENV_PATH)/bin/flake8 src/ tests/

# 清理临时文件
clean:
	rm -rf */__pycache__/ __pycache__/ src/*/__pycache__/ src/*/*/__pycache__/
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf build/ dist/ *.egg-info/

# 卸载
uninstall:
	rm -rf $(VENV_PATH)/
