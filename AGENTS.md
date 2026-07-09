# AGENTS.md

## Назначение проекта

Проект — кастомные ноды ComfyUI для Beeble SwitchX.

Основные production-ноды:

```text
Beeble SwitchX Image
Beeble SwitchX Video
```

Дополнительно в репозитории есть маленькие test/debug-ноды для проверки отдельных шагов Beeble API.

Локальная документация по API лежит в:

```text
doc/
```

Если проект используется внутри ComfyUI, ожидаемый путь такой:

```text
ComfyUI/custom_nodes/comfyui-beeble-switchx/
```

---

## Текущее состояние

На текущий момент уже готовы и протестированы:

```text
Image: auto | fill | select | custom
Video: auto | fill | select | custom
```

Что уже реализовано:

```text
полный upload -> generation -> polling -> download flow
.env support для BEEBLE_API_KEY
retry для временных network/SSL ошибок
короткие production-логи
video result работает через file path, а не через полный BytesIO в память
runtime-папка для временных video-файлов очищается при старте ComfyUI
fallback для alpha_video, если Beeble не вернул отдельный alpha result
```

Что пока остается ограничением:

```text
dynamic UI не реализован
workflow-примеры есть, но это не полная документация
валидация media в основном опирается на ответы Beeble API
```

---

## Границы работы

Работать только внутри этого проекта.

Если проект открыт как часть локального ComfyUI, без явного разрешения нельзя изменять:

```text
ComfyUI core
ComfyUI/comfy/
ComfyUI/nodes.py
другие custom_nodes
ComfyUI/input/
ComfyUI/output/
ComfyUI/models/
```

Нельзя:

```text
менять ядро ComfyUI
менять чужие custom nodes
удалять или чистить пользовательские файлы
ломать рабочее окружение пользователя
```

---

## Среда запуска

ComfyUI запускается пользователем вручную через virtualenv.

Примеры:

```bash
cd /path/to/ComfyUI
source venv/bin/activate
python main.py
```

или:

```bash
cd /path/to/ComfyUI
source .venv/bin/activate
python main.py
```

Codex не должен сам запускать, останавливать или перезапускать ComfyUI без прямой команды пользователя.

После изменений пользователь сам перезапускает ComfyUI.

Для быстрой локальной проверки использовать:

```bash
python -m compileall custom_nodes/comfyui-beeble-switchx
```

или, если открыт standalone-репозиторий:

```bash
python3 -m compileall beeble_switchx __init__.py
```

---

## Архитектурные правила

ComfyUI-ноды должны быть тонкими обертками.

Основная логика должна жить в обычных Python-модулях и переиспользоваться.

Предпочтительный путь разработки:

```text
чистая функция
→ маленькая test-нода или script test
→ ручная проверка в ComfyUI
→ переиспользование функции в production-node
```

Нельзя копировать код из test-нод в production-ноды.

Test-нода и production-нода должны вызывать одну и ту же функцию там, где это разумно.

Предпочтительное разделение ответственности:

```text
api/upload/generation/polling — работа с Beeble API
media/masks — конвертация IMAGE, MASK, VIDEO и файлов
errors — проектные ошибки
nodes — ComfyUI wrappers
scripts — тесты без интерфейса
test_workflows — ручные workflow-примеры
```

---

## Beeble flow

Beeble SwitchX работает через загруженные файлы.

Базовый процесс:

```text
локальный файл
→ create upload URL
→ upload file
→ получить beeble:// URI
→ start generation
→ poll job status
→ download result
→ вернуть результат в ComfyUI
```

Не считать, что Beeble принимает ComfyUI tensors напрямую.

Для video-ветки источник считать видеофайлом:

```text
MP4/MOV
```

Не считать video как image sequence без явной причины.

---

## Поведение production-нод

### Image

`Beeble SwitchX Image` работает с:

```text
IMAGE
reference IMAGE optional
MASK optional
alpha_mode: auto | fill | select | custom
prompt
seed
max_resolution
timeout_seconds
poll_interval_seconds
```

Для `select` и `custom` маска обязательна и уходит в Beeble как grayscale `alpha_uri`.

### Video

`Beeble SwitchX Video` работает с:

```text
VIDEO
reference IMAGE optional
alpha_keyframe_mask: MASK optional
alpha_video: VIDEO optional
alpha_keyframe_index: INT
alpha_mode: auto | fill | select | custom
prompt
seed
max_resolution
timeout_seconds
poll_interval_seconds
```

Правила:

```text
select → требует alpha_keyframe_mask
custom → требует alpha_video
alpha_keyframe_index >= 0
если alpha_video не вернулся от Beeble, нода использует основной render как fallback и пишет warning
```

Рекомендуемый пользовательский workflow для video select:

```text
LoadVideo
→ GetVideoComponents
→ ImageFromBatch
→ Painter / Mask Editor
→ Beeble SwitchX Video
→ SaveVideo
```

---

## Dynamic UI

Сложный dynamic UI пока не нужен.

Допустимы статичные optional inputs даже если часть из них актуальна только для отдельных режимов.

Если в будущем добавляется dynamic UI, он не должен ломать уже существующие workflow.

---

## API keys и секреты

Никогда не хардкодить API-ключи.

Основной способ получения ключа:

```text
BEEBLE_API_KEY
```

Текущая реализация:

```text
основной источник — .env в корне проекта
fallback — environment variable BEEBLE_API_KEY
```

Допустимо использовать явный input API key только в test/debug-нODEах.

Нельзя сохранять реальные ключи в:

```text
коде
README
workflow json
логах
комментариях
скриншотах
```

Локальные конфиги и временные папки должны быть в `.gitignore`.

---

## Ошибки и логирование

Использовать понятные проектные ошибки.

Для логов использовать `logging`, а не случайные `print()`.

Для test-нод допустим более подробный лог полезных debug-данных.

Для production-нод логировать только:

```text
короткие статусы
понятные ошибки
warning'и, которые реально помогают пользователю
```

Не писать в production-логи полные дампы API-ответов без явной причины.

Не логировать:

```text
API keys
tokens
credentials
presigned URLs целиком
секреты
```

Хорошие пользовательские ошибки должны объяснять:

```text
что сломалось
на каком шаге
что проверить пользователю
```

---

## Валидация

Не отправлять заведомо невалидные данные в Beeble API.

Проверять обязательные входы до API-запроса.

Пример:

```python
if alpha_mode == "select" and alpha_keyframe_mask is None:
    raise ValueError("alpha_keyframe_mask is required when alpha_mode='select'")
```

Для пользовательских ошибок использовать `ValueError`.

Для ошибок выполнения использовать проектные ошибки или понятные `RuntimeError` только если проектная ошибка не нужна.

---

## Зависимости

Держать зависимости минимальными.

Не добавлять тяжелые зависимости без явного смысла и согласования.

Перед добавлением зависимости:

```text
проверить, нужна ли она
добавить в requirements.txt
кратко объяснить зачем
```

Не делать широкие апдейты окружения.

---

## Тестирование

Ручное тестирование в интерфейсе ComfyUI — обязательная часть процесса.

Если после выполненного шага его можно проверить через ComfyUI, Codex должен дать короткую пошаговую инструкцию для такой проверки.

Минимальные workflow-примеры сохранять в:

```text
test_workflows/
```

Примеры workflow в репозитории — это именно reference-примеры, а не полная документация.

---

## Публикация репозитория

Проект уже опубликован как отдельный GitHub-репозиторий.

Для пользователя важны:

```text
README.md
LICENSE
.env.example
test_workflows/
```

При подготовке изменений к публикации не забывать, что локальная рабочая папка внутри ComfyUI и отдельный опубликованный standalone-репозиторий могут существовать раздельно.

---

## Безопасность команд

Не выполнять разрушительные команды без явного разрешения:

```bash
rm -rf
git reset --hard
git clean -fd
pip install --upgrade *
brew install ...
```

Не менять пользовательское окружение без прямой команды.

---

## Зафиксированные решения

Пока пользователь не скажет иначе:

```text
Codex работает только внутри comfyui-beeble-switchx
ComfyUI запускается пользователем вручную через virtualenv
ядро ComfyUI не изменяем
чужие custom nodes не изменяем
API-логику отделяем от node wrappers
разработка идет через маленькие test-ноды
Beeble video считаем видеофайлом, не image sequence
video select использует одну keyframe-mask и alpha_keyframe_index
dynamic UI не нужен в первой стабильной версии
static optional inputs допустимы для MVP
API keys не хранятся в коде
production-ноды уже опубликованы в отдельном GitHub-репозитории
```
