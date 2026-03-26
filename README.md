# QQBotManager

QQBotManager 是一个基于 Python 的 QQ 机器人管理工具，支持通过 DeepSeek API 等大模型实现自动回复功能。

## 功能

- 自动回复 QQ 消息
- 支持 DeepSeek API
- 可配置的模型参数
- 简单易用的用户界面

## 环境要求

- Windows 操作系统
- Python 3.10 或更高版本
- 已安装 Git

## 安装步骤

### 1. 克隆项目

```bash
# 使用 Git 克隆项目
https://github.com/hzqisora/QQAIBOT.git
```

### 2. 安装依赖

```bash
# 进入项目目录
cd QQBotManager

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

- 打开 `config.json` 文件，填写以下信息：
  - `api_key`: DeepSeek API 的密钥
  - `api_base_url`: DeepSeek API 的基础地址
  - 其他相关配置项

### 4. 运行

```bash
python main.py
```

## 打包为 EXE

如果需要将项目打包为 EXE 文件，可以使用以下步骤：

1. 安装 PyInstaller：

```bash
pip install pyinstaller
```

2. 运行打包命令：

```bash
pyinstaller --onefile --noconsole main.py
```

3. 打包完成后，生成的 EXE 文件位于 `dist` 文件夹中。

## 常见问题

### 1. 无法初始化 Qt 平台插件

如果运行 EXE 文件时出现以下错误：

```
This application failed to start because no Qt platform plugin could be initialized.
```

请确保将 `PyQt` 的相关依赖文件一并打包。

### 2. 无法自动回复

- 确保 DeepSeek API 配置正确。
- 检查日志文件，确认消息是否被正确接收。

### 3. NapcatQQ 使用问题

- 确保按照步骤正确配置网络和 API 信息。
- 检查 NapcatQQ 日志，确认是否有错误提示。

## 使用 NapcatQQ

NapcatQQ 是一个 QQ 机器人框架，以下是完整的使用步骤：

1. **打开 NapcatQQ**
   - 运行 NapcatQQ 的批处理文件。
   - 登录需要绑定的 QQ 号。
2. **登录 WebUI**
   - 找到 NapcatQQ 提供的 Token，登录 WebUI。
3. **配置网络**
   - 在 WebUI 中选择网络配置。
   - 选择 `WebSocket 客户端` 模式。
   - 填写以下信息：
     - **消息格式**：`ARRAY`
     - **心跳间隔**：`30` 秒（推荐）
     - **Token**：留空或填写你的自定义 Token。
     - **Host、Port**：与软件中WebSocket地址对应，例：ws://127.0.0.1:3001，Host就填127.0.0.1，Port就填3001

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 MIT 许可证。
