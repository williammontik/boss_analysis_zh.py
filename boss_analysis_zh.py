<!-- === START WIDGET FOR BOSS (ZH 中文版) === -->

<!-- 1) 样式 -->
<style>
  @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  #hiddenFormBoss {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s ease;
    display: none;
  }
  #hiddenFormBoss.show {
    display: block;
    opacity: 1;
    transform: translateY(0);
  }
  #loadingMessageBoss { display: none; text-align: center; margin-top: 30px; }
  #resultContainerBoss {
    display: none;
    opacity: 0;
    transition: opacity 0.5s ease;
    margin-top: 20px;
  }
  #resultContainerBoss.show {
    display: block;
    opacity: 1;
  }
</style>

<!-- 2) 下一步按钮 -->
<button id="simulateBossButton" style="padding:10px 20px; background:#5E9CA0; color:#fff; border:none; border-radius:8px; cursor:pointer; margin-bottom:20px;">下一步</button>

<!-- 3) 隐藏表单 -->
<div id="hiddenFormBoss" style="margin-top:20px;">
  <!-- PDPA 信息框 -->
  <div style="margin-bottom:20px; font-size:16px; line-height:1.6; background:#f9f9f9; padding:20px; border-radius:8px; border-left:6px solid #5E9CA0;">
    <p style="font-size:18px; font-weight:bold; color:#5E9CA0;">我们致力于通过真实洞察提升职场表现 😊。为了提供更好的支持，请填写以下资料。</p>
    <p style="margin-top:10px;"><strong>填写后，您将获得：</strong></p>
    <ul style="margin:10px 0 0 20px; padding:0;">
      <li><strong>基于真实数据的 AI 反馈</strong>，聚焦您的区域。</li>
      <li><strong>个性化分析报告</strong>，应对具体挑战。</li>
      <li><strong>提交前请勾选 PDPA 数据授权</strong>。</li>
    </ul>
    <p style="font-style:italic; margin-top:10px;">所有信息将受到保护，您可随时更新或删除。👍</p>
  </div>

  <!-- PDPA 勾选框 -->
  <div style="margin-bottom:20px; display:flex; align-items:center; font-size:16px;">
    <input type="checkbox" id="pdpaCheckboxBoss" style="margin-right:10px;">
    <label for="pdpaCheckboxBoss">我同意根据新加坡、马来西亚和台湾的 PDPA 隐私规范提交资料。</label>
  </div>

  <!-- 表单 -->
  <form id="bossForm" method="POST" style="display:flex; flex-direction:column; gap:20px; pointer-events:none; opacity:0.3;">
    <input type="hidden" name="lang" value="zh">

    <label for="memberName">👤 员工英文全名</label>
    <input type="text" id="memberName" required disabled style="padding:12px;">

    <label for="memberNameCn">🈶 中文名</label>
    <input type="text" id="memberNameCn" disabled style="padding:12px;">

    <label for="position">🏢 职位</label>
    <input type="text" id="position" required disabled style="padding:12px;">

    <label for="department">📂 部门（可选）</label>
    <input type="text" id="department" disabled style="padding:12px;">

    <label for="experience">🗓️ 从业年数</label>
    <input type="number" id="experience" required min="0" disabled style="padding:12px;">

    <label for="sector">📌 所属领域</label>
    <select id="sector" required disabled style="padding:12px;">
      <option value="">📌 选择领域</option>
      <option>室内 – 行政 / 人事 / 财务 / 营运</option>
      <option>室内 – 技术 / 工程 / IT</option>
      <option>户外 – 销售 / 商务拓展 / 零售</option>
      <option>户外 – 客户服务 / 物流 / 外勤</option>
    </select>

    <label for="challenge">⚠️ 面临的挑战</label>
    <textarea id="challenge" maxlength="200" required disabled style="padding:12px;"></textarea>

    <label for="focus">🌟 优先关注方向</label>
    <input type="text" id="focus" required disabled style="padding:12px;">

    <label for="email">📧 电子邮箱</label>
    <input type="email" id="email" required disabled style="padding:12px;">

    <label for="country">🌍 所在国家</label>
    <select id="country" required disabled style="padding:12px;">
      <option value="">🌍 选择国家</option>
      <option>新加坡</option>
      <option>马来西亚</option>
      <option>台湾</option>
    </select>

    <label>📅 出生日期</label>
    <div style="display:flex; gap:10px;">
      <select id="dob_day" required disabled style="flex:1; padding:12px;"><option value="">日</option></select>
      <select id="dob_month" required disabled style="flex:1; padding:12px;"><option value="">月</option></select>
      <select id="dob_year" required disabled style="flex:1; padding:12px;"><option value="">年</option></select>
    </div>

    <label for="referrer">💬 推荐人（如有）</label>
    <input type="text" id="referrer" disabled style="padding:12px;">

    <label for="contactNumber">📞 汇报对象姓名与联系方式</label>
    <input type="text" id="contactNumber" required disabled style="padding:12px;">

    <button type="submit" id="submitButtonBoss" disabled style="padding:14px; background:#5E9CA0; color:#fff; border:none; border-radius:10px; cursor:pointer;">
      🚀 提交
    </button>
  </form>
</div>

<!-- 4) 加载动画 -->
<div id="loadingMessageBoss">
  <div style="width:60px; height:60px; border:6px solid #ccc; border-top:6px solid #5E9CA0; border-radius:50%; animation:spin 1s linear infinite; margin:0 auto;"></div>
  <p style="color:#5E9CA0; margin-top:10px;">🔄 正在分析，请稍候…</p>
</div>

<!-- 5) 结果显示 -->
<div id="resultContainerBoss">
  <br><br>
  <h4 style="text-align:center; font-size:28px; font-weight:bold; color:#5E9CA0;">🎉 AI 员工表现洞察：</h4>
  <br><br>
  <div id="bossResultContent" style="white-space:pre-wrap; font-size:16px; line-height:1.6; max-width:700px; margin:0 auto;"></div>
  <div style="text-align:center; margin-top:20px;">
    <button id="resetButton" style="padding:14px; background:#2196F3; color:#fff; border:none; border-radius:10px; cursor:pointer;">🔄 重新开始</button>
  </div>
</div>

<!-- 6) Script -->
<script>
document.addEventListener('DOMContentLoaded', () => {
  const simulateBtn = document.getElementById('simulateBossButton');
  const formWrapper = document.getElementById('hiddenFormBoss');
  const form = document.getElementById('bossForm');
  const pdpa = document.getElementById('pdpaCheckboxBoss');
  const spinner = document.getElementById('loadingMessageBoss');
  const resultDiv = document.getElementById('resultContainerBoss');
  const resultContent = document.getElementById('bossResultContent');

  simulateBtn.addEventListener('click', () => {
    formWrapper.classList.add('show');
  });

  pdpa.addEventListener('change', () => {
    const fields = form.querySelectorAll('input, select, textarea, button[type="submit"]');
    fields.forEach(f => f.disabled = !pdpa.checked);
    form.style.opacity = pdpa.checked ? '1' : '0.3';
    form.style.pointerEvents = pdpa.checked ? 'auto' : 'none';
  });

  const daySel = document.getElementById('dob_day');
  for (let d = 1; d <= 31; d++) daySel.innerHTML += `<option>${d}</option>`;
  const monthSel = document.getElementById('dob_month');
  ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    .forEach(m => monthSel.innerHTML += `<option>${m}</option>`);
  const yearSel = document.getElementById('dob_year');
  const thisYear = new Date().getFullYear();
  for (let y = thisYear - 65; y <= thisYear - 18; y++) yearSel.innerHTML += `<option>${y}</option>`;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    spinner.style.display = 'block';
    resultDiv.style.display = 'none';
    resultContent.innerHTML = '';

    const getVal = id => document.getElementById(id).value;
    const payload = {
      memberName: getVal('memberName'),
      memberNameCn: getVal('memberNameCn'),
      position: getVal('position'),
      department: getVal('department'),
      experience: getVal('experience'),
      sector: getVal('sector'),
      challenge: getVal('challenge'),
      focus: getVal('focus'),
      email: getVal('email'),
      country: getVal('country'),
      dob_day: getVal('dob_day'),
      dob_month: getVal('dob_month'),
      dob_year: getVal('dob_year'),
      referrer: getVal('referrer'),
      contactNumber: getVal('contactNumber'),
      lang: 'zh'
    };

    try {
      const res = await fetch('https://boss-analysis-api.onrender.com/boss_analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      spinner.style.display = 'none';
      resultDiv.style.display = 'block';
      resultDiv.classList.add('show');

      resultContent.innerHTML = data.error
        ? `<p style="color:red;">⚠️ ${data.error}</p>`
        : data.analysis;

      // Disable form after result shown
      form.querySelectorAll('input, select, textarea, button').forEach(el => el.disabled = true);
      form.style.opacity = '0.3';
      form.style.pointerEvents = 'none';

    } catch (err) {
      console.error(err);
      spinner.style.display = 'none';
      resultDiv.style.display = 'block';
      resultContent.innerHTML = '<p style="color:red;">⚠️ Network/server error – check console.</p>';
    }
  });

  const resetBtn = document.getElementById('resetButton');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      window.location.href = "https://katachat.online";
    });
  }
});
</script>

<!-- === END WIDGET FOR BOSS (ZH) === -->
