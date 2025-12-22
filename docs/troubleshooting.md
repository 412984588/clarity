# 常见问题排查指南

## 后端问题

### 数据库连接失败

**现象**：`/health` 返回 `{"database":"error"}`

**排查步骤**：

1. 检查 Docker 容器是否运行：
   ```bash
   docker ps | grep postgres
   ```

2. 检查端口是否被占用：
   ```bash
   lsof -i :5432
   ```

3. 检查 `.env` 中的 `DATABASE_URL` 是否正确

**解决方案**：
```bash
# 重启数据库容器
docker-compose down
docker-compose up -d db
```

### Alembic 迁移失败

**现象**：`alembic upgrade head` 报错

**常见原因**：
- 数据库未启动
- 模型与现有表结构冲突

**解决方案**：
```bash
# 检查当前迁移状态
poetry run alembic current

# 重置数据库（开发环境）
docker-compose down -v
docker-compose up -d db
poetry run alembic upgrade head
```

### Poetry 安装问题

**现象**：`poetry install` 失败

**解决方案**：
```bash
# 清除缓存重试
poetry cache clear . --all
poetry install --no-root
```

## 移动端问题

### Metro Bundler 启动失败

**现象**：`npx expo start` 报错

**解决方案**：
```bash
# 清除缓存
npx expo start --clear

# 或重装依赖
rm -rf node_modules
npm install
```

### iOS 模拟器无法启动

**现象**：按 `i` 没反应

**解决方案**：
1. 确保 Xcode 已安装并打开过一次
2. 安装 iOS 模拟器：`xcode-select --install`

### Android 模拟器无法启动

**现象**：按 `a` 报错

**解决方案**：
1. 确保 Android Studio 已安装
2. 确保有可用的 AVD（Android Virtual Device）
3. 设置环境变量 `ANDROID_HOME`

### ESLint 报错

**现象**：`npm run lint` 失败

**常见错误**：
- `react/react-in-jsx-scope` - 已在配置中禁用
- 缺少 peer dependencies

**解决方案**：
```bash
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm run lint:fix
```

## 端口占用

### 8000 端口被占用

```bash
# 查找占用进程
lsof -i :8000

# 终止进程
kill -9 <PID>
```

### 5432 端口被占用

```bash
# 停止本地 PostgreSQL
brew services stop postgresql

# 或使用其他端口（修改 docker-compose.yml）
```

## 获取帮助

如果以上方案都无法解决问题：
1. 检查 GitHub Issues
2. 查看项目 Wiki
3. 联系团队成员
