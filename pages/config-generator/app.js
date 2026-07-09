const versionSelect = document.getElementById('version-select');
const versionDescription = document.getElementById('version-description');
const configForm = document.getElementById('config-form');
const jsonPreview = document.getElementById('json-preview');
const downloadConfigBtn = document.getElementById('download-config');
const downloadMainBtn = document.getElementById('download-main');
const buildHint = document.getElementById('build-hint');
const refreshPreviewBtn = document.getElementById('refresh-preview');
const copyPreviewBtn = document.getElementById('copy-preview');
const helpDialog = document.getElementById('help-dialog');
const helpDialogTitle = document.getElementById('help-dialog-title');
const helpDialogContent = document.getElementById('help-dialog-content');
const helpDialogClose = document.getElementById('help-dialog-close');

let schema = null;
let keycodes = [];

function parseVersionNumber(versionId) {
  const match = /^v_(\d+)$/.exec(versionId);
  return match ? Number(match[1]) : 0;
}

function getSelectedVersionNumber() {
  return parseVersionNumber(versionSelect.value);
}

function getNestedValue(obj, path) {
  return path.split('.').reduce((acc, key) => (acc == null ? undefined : acc[key]), obj);
}

function setNestedValue(obj, path, value) {
  const keys = path.split('.');
  let current = obj;
  for (let i = 0; i < keys.length - 1; i += 1) {
    if (typeof current[keys[i]] !== 'object' || current[keys[i]] === null) {
      current[keys[i]] = {};
    }
    current = current[keys[i]];
  }
  current[keys[keys.length - 1]] = value;
}

function parseControlValue(element) {
  if (element.type === 'checkbox') {
    return element.checked;
  }

  const raw = element.value.trim();
  if (raw === '') return undefined;

  if (element.dataset.valueType === 'number') {
    return Number(raw);
  }

  return raw;
}

function getFormValues() {
  const values = {};
  configForm.querySelectorAll('[data-key]').forEach((element) => {
    if (element.closest('.hidden')) return;

    const key = element.dataset.key;
    if (!key) return;

    const value = parseControlValue(element);
    if (value === undefined) return;

    setNestedValue(values, key, value);
  });
  return values;
}

function getScreenerValue(values) {
  const versionNum = getSelectedVersionNumber();
  if (versionNum < 5) return 'telegram';
  return values.screener || 'telegram';
}

function getPrinterValue(values) {
  const versionNum = getSelectedVersionNumber();
  if (versionNum < 5) return values.printer || 'telegram';
  return values.printer || 'telegram';
}

function needsProvider(values, provider) {
  const versionNum = getSelectedVersionNumber();
  if (versionNum < 5) return provider === 'telegram';
  return getScreenerValue(values) === provider || getPrinterValue(values) === provider;
}

function blockMatchesVersion(block, versionNum) {
  const min = block.minVersion ?? 0;
  const max = block.maxVersion ?? 99;
  return versionNum >= min && versionNum <= max;
}

function blockMatchesConditions(block, values) {
  const versionNum = getSelectedVersionNumber();
  const screener = getScreenerValue(values);

  if (block.showWhenProvider) {
    if (versionNum < 5) {
      return block.showWhenProvider === 'telegram';
    }
    return needsProvider(values, block.showWhenProvider);
  }

  if (!block.showWhen) return true;

  if (block.showWhen.screener && versionNum >= 5 && block.showWhen.screener !== screener) {
    return false;
  }

  return true;
}

function fieldMatchesVersion(field, versionNum) {
  const min = field.minVersion ?? 0;
  return versionNum >= min;
}

function shouldShowBlock(block) {
  const versionNum = getSelectedVersionNumber();
  if (!blockMatchesVersion(block, versionNum)) return false;
  return blockMatchesConditions(block, getFormValues());
}

function formatKeyOptionLabel(item) {
  const hint = item.hint ? ` — ${item.hint}` : '';
  return `${item.label} (${item.value})${hint}`;
}

function openHelp(helpId) {
  const instruction = schema.instructions?.[helpId];
  if (!instruction) return;

  helpDialogTitle.textContent = instruction.title;
  helpDialogContent.replaceChildren();

  const list = document.createElement('ol');
  list.className = 'help-steps';
  instruction.steps.forEach((step) => {
    const item = document.createElement('li');
    item.textContent = step;
    list.appendChild(item);
  });
  helpDialogContent.appendChild(list);
  helpDialog.showModal();
}

function createHelpButton(helpId) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'btn-help';
  button.textContent = 'как получить';
  button.addEventListener('click', () => openHelp(helpId));
  return button;
}

function createFieldElement(field) {
  const wrapper = document.createElement('div');
  wrapper.className = field.type === 'checkbox' ? 'field field--checkbox' : 'field';
  wrapper.dataset.keyWrapper = field.key;

  const labelRow = document.createElement('div');
  labelRow.className = 'field__label-row';

  const label = document.createElement('span');
  label.className = 'field__label';
  label.textContent = field.label;
  labelRow.appendChild(label);

  if (field.help) {
    labelRow.appendChild(createHelpButton(field.help));
  }

  let control;

  if (field.type === 'keyselect') {
    control = document.createElement('select');
    control.className = 'field__control';
    control.dataset.valueType = 'number';
    keycodes.forEach((item) => {
      const opt = document.createElement('option');
      opt.value = String(item.value);
      opt.textContent = formatKeyOptionLabel(item);
      control.appendChild(opt);
    });
    if (field.default != null) {
      control.value = String(field.default);
    }
  } else if (field.type === 'select') {
    control = document.createElement('select');
    control.className = 'field__control';
    field.options.forEach((option) => {
      const opt = document.createElement('option');
      opt.value = option.value;
      opt.textContent = option.label;
      control.appendChild(opt);
    });
    if (field.default != null) {
      control.value = String(field.default);
    }
  } else if (field.type === 'checkbox') {
    control = document.createElement('input');
    control.type = 'checkbox';
    control.className = 'field__control';
    control.checked = Boolean(field.default);
    wrapper.appendChild(control);
    wrapper.appendChild(labelRow);
  } else {
    control = document.createElement('input');
    control.className = 'field__control';
    control.type = field.type === 'number' ? 'number' : 'text';
    if (field.placeholder) control.placeholder = field.placeholder;
    if (field.default != null) control.value = String(field.default);
    if (field.type === 'number') control.dataset.valueType = 'number';
  }

  control.dataset.key = field.key;
  if (field.required) control.required = true;

  if (field.type !== 'checkbox') {
    wrapper.appendChild(labelRow);
    wrapper.appendChild(control);
  }

  if (field.hint) {
    const hint = document.createElement('span');
    hint.className = 'field__hint';
    hint.textContent = field.hint;
    wrapper.appendChild(hint);
  }

  control.addEventListener('input', onFormChange);
  control.addEventListener('change', onFormChange);

  return wrapper;
}

function renderForm() {
  const versionNum = getSelectedVersionNumber();
  configForm.replaceChildren();

  schema.blocks.forEach((block) => {
    if (!blockMatchesVersion(block, versionNum)) return;

    const visibleFields = block.fields.filter((field) => fieldMatchesVersion(field, versionNum));
    if (!visibleFields.length) return;

    const section = document.createElement('section');
    section.className = 'block';
    section.dataset.blockId = block.id;

    const title = document.createElement('h3');
    title.className = 'block__title';
    title.textContent = block.title;
    section.appendChild(title);

    visibleFields.forEach((field) => {
      section.appendChild(createFieldElement(field));
    });

    configForm.appendChild(section);
  });

  updateBlockVisibility();
  updateBuildHint();
}

function updateBlockVisibility() {
  configForm.querySelectorAll('.block').forEach((section) => {
    const block = schema.blocks.find((item) => item.id === section.dataset.blockId);
    const visible = block && shouldShowBlock(block);
    section.classList.toggle('hidden', !visible);
  });
  updatePreview();
}

function buildConfigObject() {
  const versionNum = getSelectedVersionNumber();
  const values = getFormValues();
  const screener = getScreenerValue(values);
  const needsTelegram = needsProvider(values, 'telegram');
  const needsVk = needsProvider(values, 'vk');
  const config = {};

  schema.blocks.forEach((block) => {
    if (!blockMatchesVersion(block, versionNum)) return;
    if (!blockMatchesConditions(block, values)) return;

    block.fields.forEach((field) => {
      if (!fieldMatchesVersion(field, versionNum)) return;

      const value = getNestedValue(values, field.key);
      if (value === undefined || value === '') return;

      if ((field.key === 'bot_token' || field.key === 'chat_id') && !needsTelegram) return;
      if (field.key.startsWith('vk.') && !needsVk) return;
      if (field.key === 'compression' && screener !== 'telegram') return;
      if (field.key.startsWith('commands_settings') && screener !== 'telegram') return;

      setNestedValue(config, field.key, value);
    });
  });

  if (versionNum >= 5) {
    config.screener = screener;
    if (values.printer) {
      config.printer = values.printer;
    }
  } else if (values.printer) {
    config.printer = values.printer;
  }

  if (!needsTelegram) {
    delete config.bot_token;
    delete config.chat_id;
  }

  if (!needsVk) {
    delete config.vk;
  }

  if (screener !== 'telegram') {
    delete config.compression;
    delete config.commands_settings;
  }

  return config;
}

function updatePreview() {
  const config = buildConfigObject();
  jsonPreview.textContent = JSON.stringify(config, null, 2);
}

function validateForm() {
  let valid = true;
  const values = getFormValues();
  const needsTelegram = needsProvider(values, 'telegram');
  const needsVk = needsProvider(values, 'vk');

  configForm.querySelectorAll('[data-key]').forEach((element) => {
    const wrapper = element.closest('[data-key-wrapper]');
    if (wrapper && wrapper.closest('.hidden')) return;

    const key = element.dataset.key;
    if (!needsTelegram && (key === 'bot_token' || key === 'chat_id')) return;
    if (!needsVk && key.startsWith('vk.')) return;

    const isEmpty = element.type === 'checkbox'
      ? false
      : element.value.trim() === '';

    const invalid = element.required && isEmpty;
    element.classList.toggle('field__control--invalid', invalid);
    if (invalid) valid = false;
  });

  return valid;
}

function onFormChange() {
  updateBlockVisibility();
}

function downloadBlob(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function getSelectedVersionMeta() {
  return schema.versions.find((item) => item.id === versionSelect.value);
}

function getBuildDownloadUrl() {
  const meta = getSelectedVersionMeta();
  if (!meta?.buildFile) return null;
  return `https://github.com/${schema.repo}/raw/${schema.branch}/${meta.buildFile}`;
}

function updateBuildHint() {
  const url = getBuildDownloadUrl();
  const meta = getSelectedVersionMeta();
  if (!url) {
    buildHint.textContent = 'Для этой версии файл сборки не указан в schema.json.';
    downloadMainBtn.disabled = true;
    downloadMainBtn.textContent = 'Скачать программу';
    return;
  }

  const filename = meta.buildFile.split('/').pop();
  downloadMainBtn.disabled = false;
  downloadMainBtn.textContent = `Скачать ${filename}`;
  buildHint.textContent = `Ссылка на файл в репозитории: ${meta.buildFile}`;
}

function onDownloadConfig() {
  if (!validateForm()) {
    jsonPreview.textContent = 'Заполните обязательные поля (подсвечены красным).';
    return;
  }
  const config = buildConfigObject();
  downloadBlob('config.json', JSON.stringify(config, null, 2) + '\n', 'application/json');
}

function onDownloadMain() {
  const url = getBuildDownloadUrl();
  if (!url) return;

  const meta = getSelectedVersionMeta();
  const filename = meta.buildFile.split('/').pop();
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  link.click();
}

async function onCopyPreview() {
  const text = jsonPreview.textContent;
  if (!text) return;

  try {
    await navigator.clipboard.writeText(text);
    const original = copyPreviewBtn.textContent;
    copyPreviewBtn.textContent = 'Скопировано';
    setTimeout(() => {
      copyPreviewBtn.textContent = original;
    }, 1500);
  } catch {
    copyPreviewBtn.textContent = 'Ошибка';
    setTimeout(() => {
      copyPreviewBtn.textContent = 'Копировать';
    }, 1500);
  }
}

function populateVersionSelect() {
  versionSelect.replaceChildren();
  schema.versions.forEach((version) => {
    const option = document.createElement('option');
    option.value = version.id;
    option.textContent = version.label;
    versionSelect.appendChild(option);
  });

  const latest = schema.versions[schema.versions.length - 1];
  versionSelect.value = latest.id;
  versionDescription.textContent = latest.description;
}

function onVersionChange() {
  const meta = getSelectedVersionMeta();
  versionDescription.textContent = meta?.description || '';
  renderForm();
}

async function init() {
  const [schemaResponse, keycodesResponse] = await Promise.all([
    fetch('schema.json'),
    fetch('keycodes.json'),
  ]);

  schema = await schemaResponse.json();
  keycodes = await keycodesResponse.json();

  populateVersionSelect();
  renderForm();

  versionSelect.addEventListener('change', onVersionChange);
  downloadConfigBtn.addEventListener('click', onDownloadConfig);
  downloadMainBtn.addEventListener('click', onDownloadMain);
  refreshPreviewBtn.addEventListener('click', updatePreview);
  copyPreviewBtn.addEventListener('click', onCopyPreview);
  helpDialogClose.addEventListener('click', () => helpDialog.close());
  helpDialog.addEventListener('click', (event) => {
    if (event.target === helpDialog) {
      helpDialog.close();
    }
  });
}

init().catch((error) => {
  jsonPreview.textContent = `Ошибка загрузки: ${error.message}`;
});
