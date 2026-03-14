const form = document.getElementById("publish-form");
const promptInput = document.getElementById("prompt-input");
const submitButton = document.getElementById("submit-button");
const healthPill = document.getElementById("health-pill");
const resultBadge = document.getElementById("result-badge");
const timelineText = document.getElementById("timeline-text");
const resultStatus = document.getElementById("result-status");
const resultTitle = document.getElementById("result-title");
const resultSite = document.getElementById("result-site");
const resultContent = document.getElementById("result-content");
const resultImage = document.getElementById("result-image");
const imagePlaceholder = document.getElementById("image-placeholder");
const chips = document.querySelectorAll(".chip");

function setBusyState(isBusy) {
  submitButton.disabled = isBusy;
  submitButton.classList.toggle("loading", isBusy);
}

function setHealthState({ ok, has_login_state, is_busy }) {
  healthPill.className = "status-pill";
  if (!ok) {
    healthPill.textContent = "服务异常";
    healthPill.classList.add("missing");
    return;
  }

  if (is_busy) {
    healthPill.textContent = "当前有任务执行中";
    healthPill.classList.add("busy");
    return;
  }

  if (has_login_state) {
    healthPill.textContent = "已保存登录态";
    healthPill.classList.add("ready");
  } else {
    healthPill.textContent = "首次发布需登录";
    healthPill.classList.add("missing");
  }
}

function setResultTone(tone, label) {
  resultBadge.className = "result-badge";
  if (tone) {
    resultBadge.classList.add(tone);
  }
  resultBadge.textContent = label;
}

function renderImage(imageUrl) {
  if (!imageUrl) {
    resultImage.hidden = true;
    resultImage.removeAttribute("src");
    imagePlaceholder.hidden = false;
    return;
  }

  resultImage.src = imageUrl;
  resultImage.hidden = false;
  imagePlaceholder.hidden = true;
}

function renderResult(result) {
  resultStatus.textContent = result.output || "流程已完成";
  resultTitle.textContent = result.title || "-";
  resultSite.textContent = result.site || "-";
  resultContent.textContent = result.content || "未返回正文内容";
  renderImage(result.image_urls?.[0]);

  if (result.published) {
    setResultTone("success", "发布完成");
    timelineText.textContent = "任务已跑完，浏览器已尝试完成真实发布。";
  } else {
    setResultTone("error", "任务结束");
    timelineText.textContent = "任务已执行完成，但结果不是成功发布，请查看状态信息。";
  }
}

async function fetchHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    setHealthState(data);
  } catch (error) {
    setHealthState({ ok: false });
  }
}

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    promptInput.value = chip.dataset.prompt || "";
    promptInput.focus();
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = promptInput.value.trim();

  if (!text) {
    setResultTone("error", "缺少输入");
    timelineText.textContent = "先输入一个主题文本，再开始自动发布。";
    resultStatus.textContent = "请输入主题";
    return;
  }

  setBusyState(true);
  setResultTone("running", "任务执行中");
  timelineText.textContent = "后台正在生成文案和图片。如果首次发布，浏览器会在本机打开，请完成登录后等待自动继续。";
  resultStatus.textContent = "正在执行发布流程";
  resultTitle.textContent = "-";
  resultSite.textContent = "-";
  resultContent.textContent = "请稍候，文案与配图生成中。";
  renderImage(null);

  try {
    const response = await fetch("/api/publish", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "请求失败");
    }

    renderResult(payload);
  } catch (error) {
    setResultTone("error", "执行失败");
    timelineText.textContent = "本次发布流程提前结束。";
    resultStatus.textContent = error.message;
    resultContent.textContent = "你可以检查浏览器登录状态、接口密钥或页面元素是否变更后再重试。";
    renderImage(null);
  } finally {
    setBusyState(false);
    fetchHealth();
  }
});

fetchHealth();
