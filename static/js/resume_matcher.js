/**
 * AI Resume & Skill Gap Analyzer Client Tool
 */

document.addEventListener('DOMContentLoaded', () => {
  const analyzeBtn = document.getElementById('btn-run-analyzer');
  if (!analyzeBtn) return;

  const skillsInput = document.getElementById('analyzer-skills-input');
  const roleSelect = document.getElementById('analyzer-role-select');
  const jobSelect = document.getElementById('analyzer-job-select');
  const resultCard = document.getElementById('analyzer-result-card');

  analyzeBtn.addEventListener('click', () => {
    const skills = skillsInput ? skillsInput.value : '';
    const jobId = jobSelect ? jobSelect.value : '';
    const customRole = roleSelect ? roleSelect.value : '';

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="pulse">🤖 Analyzing Skill Alignment...</span>';

    fetch('/api/analyze-resume', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        skills: skills,
        job_id: jobId,
        custom_role: customRole
      })
    })
    .then(res => res.json())
    .then(data => {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '<span>⚡ Analyze Readiness Score</span>';
      
      if (resultCard) {
        resultCard.style.display = 'block';
        resultCard.scrollIntoView({ behavior: 'smooth' });

        // Update Score Elements
        const scoreElem = document.getElementById('res-match-score');
        const badgeElem = document.getElementById('res-readiness-badge');
        const matchedList = document.getElementById('res-matched-tags');
        const missingList = document.getElementById('res-missing-tags');
        const tipsList = document.getElementById('res-recommendations-list');

        if (scoreElem) scoreElem.textContent = `${data.match_percentage}%`;
        if (badgeElem) {
          badgeElem.textContent = data.readiness_badge;
          badgeElem.className = `badge badge-${data.badge_color || 'emerald'}`;
        }

        // Render Matched Tags
        if (matchedList) {
          matchedList.innerHTML = '';
          (data.matched_skills || []).forEach(skill => {
            const span = document.createElement('span');
            span.className = 'badge badge-core';
            span.innerHTML = `✓ ${skill}`;
            matchedList.appendChild(span);
          });
          if (!data.matched_skills || data.matched_skills.length === 0) {
            matchedList.innerHTML = '<span style="color:#94a3b8; font-size:0.85rem;">No exact keyword matches found.</span>';
          }
        }

        // Render Missing Tags
        if (missingList) {
          missingList.innerHTML = '';
          (data.missing_skills || []).forEach(skill => {
            const span = document.createElement('span');
            span.className = 'badge badge-mass';
            span.innerHTML = `+ ${skill}`;
            missingList.appendChild(span);
          });
          if (!data.missing_skills || data.missing_skills.length === 0) {
            missingList.innerHTML = '<span style="color:#34d399; font-size:0.85rem;">All primary requirements covered!</span>';
          }
        }

        // Render Recommendations
        if (tipsList) {
          tipsList.innerHTML = '';
          (data.recommendations || []).forEach(tip => {
            const li = document.createElement('li');
            li.style.marginBottom = '0.5rem';
            li.innerHTML = tip;
            tipsList.appendChild(li);
          });
        }
      }
    })
    .catch(err => {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '<span>⚡ Analyze Readiness Score</span>';
      alert('Error analyzing profile. Please check inputs and try again.');
    });
  });
});
