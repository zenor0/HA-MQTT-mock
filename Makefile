.PHONY: install run test lint format clean uninstall dev-install

# 安装依赖
install:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

# 开发模式安装
dev-install:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -e .

# 运行程序
run:
	venv/bin/python -m ha_mqtt_mock.main

# 运行测试
test:
	venv/bin/pytest tests/

# 代码格式化
format:
	venv/bin/black src/ tests/
	venv/bin/isort src/ tests/

# 代码检查
lint:
	venv/bin/flake8 src/ tests/

# 清理临时文件
clean:
	rm -rf */__pycache__/ __pycache__/ src/*/__pycache__/ src/*/*/__pycache__/
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf build/ dist/ *.egg-info/

# 卸载
uninstall:
	rm -rf venv/
