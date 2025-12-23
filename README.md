# 天气预报机器人 (Weather Forecast Bot)

这是一个轻量级的天气预报机器人，每天自动获取南京天气信息，进行趋势分析，并通过 Server酱 推送通知。

## 功能特点

- 🌤️ 每天定时获取南京明日天气预报
- 📊 分析最近7天的天气趋势
- 📱 通过 Server酱 发送微信通知
- 💾 自动保存历史数据并进行清理
- ⚡ 轻量快速，运行时间约1分钟
- 🤖 完全自动化，通过 GitHub Actions 部署

## GitHub Actions 部署

本项目已配置 GitHub Actions 工作流，实现每日自动执行。

### 工作流配置

工作流文件位于 `.github/workflows/daily-weather-forecast.yml`

**执行时间：**
- 每天 UTC 00:00（北京时间 08:00）自动运行
- 支持手动触发（Manual trigger）

**主要步骤：**
1. 检出代码
2. 设置 Python 3.10 环境
3. 安装依赖包
4. 创建日志目录
5. 运行天气预报程序
6. 提交更新的数据文件
7. 推送更改到仓库

### 使用 GitHub Secrets（可选）

如果希望将 API 密钥等敏感信息从 `config.json` 中移出，可以使用 GitHub Secrets：

1. 在 GitHub 仓库页面，进入 `Settings` → `Secrets and variables` → `Actions`
2. 点击 `New repository secret` 添加以下密钥：
   - `QWEATHER_API_KEY`: 和风天气API密钥
   - `SERVERCHAN_SENDKEY`: Server酱SendKey

3. 修改 `config.json`，将敏感信息用环境变量占位
4. 在工作流文件中取消注释环境变量部分

### 手动触发工作流

1. 进入 GitHub 仓库的 `Actions` 标签页
2. 选择 `Daily Weather Forecast` 工作流
3. 点击 `Run workflow` 按钮
4. 选择分支后点击 `Run workflow` 确认

### 查看运行日志

1. 进入 `Actions` 标签页
2. 点击具体的工作流运行记录
3. 展开各个步骤查看详细日志

## 本地运行

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

编辑 `config.json` 文件，填入你的配置：

```json
{
  "qweather": {
    "api_key": "你的和风天气API密钥",
    "location_id": "101190101"
  },
  "serverchan": {
    "sendkey": "你的Server酱SendKey"
  }
}
```

### 运行

```bash
python main.py
```

## 项目结构

```
WeatherForecastBot/
├── .github/
│   └── workflows/
│       └── daily-weather-forecast.yml  # GitHub Actions 工作流
├── main.py                              # 主程序
├── data_manager.py                      # 数据管理模块
├── weather_analyzer.py                  # 天气分析模块
├── notifier.py                          # 通知模块
├── config.json                          # 配置文件
├── requirements.txt                     # Python依赖
├── weather_data.json                    # 天气数据（自动生成）
├── run_record.json                      # 运行记录（自动生成）
└── logs/                                # 日志目录（自动生成）
```

## 配置说明

### config.json 参数说明

- `qweather.api_key`: 和风天气 API 密钥（[注册获取](https://dev.qweather.com/)）
- `qweather.location_id`: 城市 ID（南京：101190101）
- `serverchan.sendkey`: Server酱 SendKey（[注册获取](https://sct.ftqq.com/)）
- `settings.execution_window`: 执行时间窗口（小时）
- `settings.data_retention_days`: 数据保留天数
- `settings.analysis_days`: 分析历史天数
- `analysis.*`: 各种天气分析阈值

## 注意事项

1. **API 配额**：和风天气免费版有每日请求限制，注意不要过度调用
2. **数据持久化**：`weather_data.json` 和 `run_record.json` 会自动提交到仓库
3. **时区设置**：工作流已设置为 Asia/Shanghai 时区
4. **运行频率**：建议每天运行一次，避免重复执行

## 故障排查

### 工作流执行失败

1. 检查 Actions 页面的详细日志
2. 确认 Python 依赖是否正确安装
3. 验证 API 密钥是否有效
4. 检查网络连接和 API 请求限制

### 通知未收到

1. 检查 Server酱 SendKey 是否正确
2. 查看程序日志中的错误信息
3. 确认 Server酱 服务状态

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
