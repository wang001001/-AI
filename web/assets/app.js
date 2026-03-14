const form = document.getElementById("publish-form");
const promptInput = document.getElementById("prompt-input");
const imageCountInput = document.getElementById("image-count-input");
const submitButton = document.getElementById("submit-button");
const healthPill = document.getElementById("health-pill");
const resultBadge = document.getElementById("result-badge");
const timelineText = document.getElementById("timeline-text");
const resultStatus = document.getElementById("result-status");
const resultTitle = document.getElementById("result-title");
const resultSite = document.getElementById("result-site");
const resultImageCount = document.getElementById("result-image-count");
const resultContent = document.getElementById("result-content");
const resultImage = document.getElementById("result-image");
const imagePlaceholder = document.getElementById("image-placeholder");
const imageGallery = document.getElementById("image-gallery");
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

function clearGallery() {
  imageGallery.innerHTML = "";
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

function renderGallery(imageUrls = []) {
  clearGallery();
  imageUrls.forEach((url, index) => {
    const thumb = document.createElement("button");
    thumb.type = "button";
    thumb.className = "gallery-thumb";
    thumb.setAttribute("aria-label", `查看第 ${index + 1} 张图片`);

    const img = document.createElement("img");
    img.src = url;
    img.alt = `第 ${index + 1} 张配图`;
    thumb.appendChild(img);

    thumb.addEventListener("click", () => {
      renderImage(url);
      document.querySelectorAll(".gallery-thumb").forEach((node) => node.classList.remove("active"));
      thumb.classList.add("active");
    });

    if (index === 0) {
      thumb.classList.add("active");
    }

    imageGallery.appendChild(thumb);
  });
}

function renderResult(result) {
  resultStatus.textContent = result.output || "流程已完成";
  resultTitle.textContent = result.title || "-";
  resultSite.textContent = result.site || "-";
  resultImageCount.textContent = result.image_count || 0;
  resultContent.textContent = result.content || "未返回正文内容";
  renderImage(result.image_urls?.[0]);
  renderGallery(result.image_urls || []);

  if (result.published) {
    setResultTone("success", "发布完成");
    timelineText.textContent = `任务已跑完，已按 ${result.image_count || 0} 张图的配置执行发布流程。`;
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
  const imageCount = Math.max(1, Math.min(5, Number(imageCountInput.value || 1)));
  imageCountInput.value = imageCount;

  if (!text) {
    setResultTone("error", "缺少输入");
    timelineText.textContent = "先输入一个主题文本，再开始自动发布。";
    resultStatus.textContent = "请输入主题";
    return;
  }

  setBusyState(true);
  setResultTone("running", "任务执行中");
  timelineText.textContent = `后台正在生成文案和图片，本次目标图片数为 ${imageCount} 张。首次发布时，浏览器会在本机打开，请完成登录后等待自动继续。`;
  resultStatus.textContent = "正在执行发布流程";
  resultTitle.textContent = "-";
  resultSite.textContent = "-";
  resultImageCount.textContent = imageCount;
  resultContent.textContent = "请稍候，文案与多张配图生成中。";
  clearGallery();
  renderImage(null);

  try {
    const response = await fetch("/api/publish", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text, image_count: imageCount }),
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
    resultContent.textContent = "你可以检查浏览器登录状态、接口密钥、页面元素或图片上传状态后再重试。";
    resultImageCount.textContent = imageCount;
    clearGallery();
    renderImage(null);
  } finally {
    setBusyState(false);
    fetchHealth();
  }
});

fetchHealth();
