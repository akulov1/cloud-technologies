import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    method = event.get("httpMethod", "GET").upper()

    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
    }

    if method == "OPTIONS":
        return {
            "statusCode": 204,
            "headers": cors_headers,
            "body": ""
        }

    # GET — отдаём HTML
    if method == "GET":
        html = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Feedback</title></head>
<body>
  <h2>Оставь сообщение</h2>
  <input id="name" placeholder="Имя"><br>
  <input id="message" placeholder="Сообщение"><br>
  <button id="sendBtn">Отправить</button>
  <p id="result"></p>

  <script>
  document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("sendBtn");
    const resEl = document.getElementById("result");
    console.log("DOM loaded");

    btn.addEventListener("click", async () => {
      const name = document.getElementById("name").value || "Аноним";
      const message = document.getElementById("message").value || "";
      const payload = { name, message };
      console.log("Отправка данных:", payload);
      btn.disabled = true;
      resEl.textContent = "Отправка...";

      try {
        const resp = await fetch(window.location.href, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        console.log("HTTP response:", resp.status, resp.statusText);
        const text = await resp.text();
        resEl.textContent = text;
      } catch (err) {
        console.error("Ошибка fetch:", err);
        resEl.textContent = "Ошибка отправки. Проверь консоль.";
      } finally {
        btn.disabled = false;
      }
    });
  });
  </script>
</body>
</html>"""
        headers = {"Content-Type": "text/html; charset=utf-8"}
        headers.update(cors_headers)
        return {"statusCode": 200, "headers": headers, "body": html}

    if method == "POST":
        body = event.get("body", "")
        try:
            data = json.loads(body) if body else {}
        except Exception as e:
            logger.exception("Не удалось распарсить JSON")
            data = {}

        name = data.get("name", "Аноним")
        message = data.get("message", "(пустое сообщение)")
        logger.info("Получено сообщение от %s: %s", name, message)

        headers = {"Content-Type": "text/plain; charset=utf-8"}
        headers.update(cors_headers)
        return {"statusCode": 200, "headers": headers, "body": f"Спасибо, {name}! Сообщение получено."}

    return {"statusCode": 405, "headers": cors_headers, "body": "Метод не поддерживается"}
