/**
 * pa Oracle Studio — app.js
 * Eye of Ma'at — Interactive frontend
 * No dependencies required
 */

(function () {
  'use strict';

  // ─── Skills Data ───
  const SKILLS = [
    { name: '/awaken',        icon: '𓋹', desc: 'Birth/initialize Oracle' },
    { name: '/recap',         icon: '𓇳', desc: 'Session orientation' },
    { name: '/rrr',           icon: '𓍯', desc: 'Session retrospective' },
    { name: '/forward',       icon: '𓊝', desc: 'Create handoff' },
    { name: '/standup',       icon: '𓅃', desc: 'Daily task check' },
    { name: '/trace',         icon: '𓐍', desc: 'Find projects & knowledge' },
    { name: '/learn',         icon: '𓉐', desc: 'Explore codebases' },
    { name: '/dig',           icon: '𓆣', desc: 'Mine past sessions' },
    { name: '/talk-to',       icon: '𓃭', desc: 'Message other Oracles' },
    { name: '/philosophy',    icon: '𓂀', desc: 'Review principles' },
    { name: '/who-are-you',   icon: '𓎡', desc: 'Check identity' },
    { name: '/oracle',        icon: '𓌙', desc: 'Manage skills' },
    { name: '/go',            icon: '𓏏', desc: 'Switch profiles' },
    { name: '/workon',        icon: '𓊝', desc: 'Work on issues' },
    { name: '/worktree',      icon: '𓉐', desc: 'Parallel git work' },
    { name: '/feel',          icon: '𓋹', desc: 'Log emotions' },
    { name: '/speak',         icon: '𓅃', desc: 'Text-to-speech' },
    { name: '/watch',         icon: '𓇳', desc: 'Learn from YouTube' },
    { name: '/deep-research', icon: '𓆣', desc: 'Deep research via Gemini' },
    { name: '/schedule',      icon: '𓍯', desc: 'Query schedule' },
    { name: '/project',       icon: '𓐍', desc: 'Clone & track repos' },
  ];

  // ─── Memory Tree Data ───
  const MEMORY_TREE = {
    name: 'ψ/',
    children: [
      { name: 'inbox/', children: [
        { name: 'messages.md', type: 'file' },
      ]},
      { name: 'memory/', children: [
        { name: 'resonance/', children: [
          { name: 'soul.md', type: 'file' },
          { name: 'principles.md', type: 'file' },
        ]},
        { name: 'learnings/', children: [
          { name: 'patterns.md', type: 'file' },
        ]},
        { name: 'retrospectives/', children: [
          { name: 'sessions.md', type: 'file' },
        ]},
        { name: 'logs/', children: [
          { name: 'snapshots.md', type: 'file' },
        ]},
      ]},
      { name: 'writing/', children: [] },
      { name: 'lab/', children: [] },
      { name: 'learn/', children: [] },
      { name: 'active/', children: [] },
      { name: 'archive/', children: [] },
      { name: 'outbox/', children: [] },
    ],
  };

  // ─── Fallback Mission Data ───
  const FALLBACK_PROJECTS = {
    version: '1.0.0',
    oracle: 'pa-oracle',
    projects: [
      {
        id: '01',
        name: 'pa-oracle',
        path: 'pa-Oracle v2',
        description: 'pa Oracle — Eye of Ma\'at 𓂀 (home base)',
        oracle: 'pa-oracle',
        status: 'active',
      },
    ],
  };

  // ─── Initialize ───
  document.addEventListener('DOMContentLoaded', function () {
    renderSkills();
    renderMemoryTree();
    renderFamilyVisual();
    loadMissionData();
    startStatusAnimation();
  });

  // ─── Skills Panel ───
  function renderSkills() {
    var grid = document.getElementById('skillsGrid');
    var countEl = document.getElementById('skillCount');
    if (!grid) return;

    countEl.textContent = SKILLS.length + ' installed';

    var html = '';
    for (var i = 0; i < SKILLS.length; i++) {
      var s = SKILLS[i];
      html += '<div class="skill-chip" title="' + escapeHtml(s.desc) + '">' +
        '<span class="skill-icon">' + s.icon + '</span>' +
        '<span class="skill-name">' + escapeHtml(s.name) + '</span>' +
        '</div>';
    }
    grid.innerHTML = html;
  }

  // ─── Mission Control ───
  function loadMissionData() {
    var body = document.getElementById('missionBody');
    if (!body) return;

    // Try loading from relative path; fall back to embedded data
    fetch('../mission-control/projects.json')
      .then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(function (data) {
        renderProjects(body, data);
      })
      .catch(function () {
        renderProjects(body, FALLBACK_PROJECTS);
      });
  }

  function renderProjects(container, data) {
    if (!data.projects || data.projects.length === 0) {
      container.innerHTML = '<div class="mission-empty">No projects registered yet.</div>';
      return;
    }

    var html = '';
    for (var i = 0; i < data.projects.length; i++) {
      var p = data.projects[i];
      var statusClass = p.status === 'active' ? 'active' : 'archived';
      html += '<div class="project-item">' +
        '<span class="project-status ' + statusClass + '"></span>' +
        '<div class="project-info">' +
        '<div class="project-name">' + escapeHtml(p.name) + '</div>' +
        '<div class="project-desc">' + escapeHtml(p.description) + '</div>' +
        '</div>' +
        '<span class="project-id">#' + escapeHtml(p.id) + '</span>' +
        '</div>';
    }
    container.innerHTML = html;
  }

  // ─── Memory Tree ───
  function renderMemoryTree() {
    var container = document.getElementById('memoryTree');
    if (!container) return;
    container.innerHTML = buildTreeHTML(MEMORY_TREE, true);
    attachTreeListeners(container);
  }

  function buildTreeHTML(node, isOpen) {
    if (node.type === 'file') {
      return '<div class="mem-file"><span class="file-icon">𓏏</span>' +
        escapeHtml(node.name) + '</div>';
    }

    var childrenHTML = '';
    if (node.children) {
      for (var i = 0; i < node.children.length; i++) {
        childrenHTML += buildTreeHTML(node.children[i], false);
      }
    }

    var openClass = isOpen ? ' open' : '';
    var arrowClass = isOpen ? 'arrow open' : 'arrow';

    return '<div class="mem-folder">' +
      '<div class="mem-folder-header">' +
      '<span class="' + arrowClass + '">&#9654;</span>' +
      '<span class="folder-icon">𓉐</span>' +
      escapeHtml(node.name) +
      '</div>' +
      '<div class="mem-children' + openClass + '">' +
      (childrenHTML || '<div class="mem-file"><span class="file-icon" style="opacity:0.3">...</span><span style="color:var(--text-muted);font-size:0.75rem">empty</span></div>') +
      '</div>' +
      '</div>';
  }

  function attachTreeListeners(container) {
    var headers = container.querySelectorAll('.mem-folder-header');
    for (var i = 0; i < headers.length; i++) {
      headers[i].addEventListener('click', function () {
        var arrow = this.querySelector('.arrow');
        var children = this.nextElementSibling;
        if (arrow && children) {
          arrow.classList.toggle('open');
          children.classList.toggle('open');
        }
      });
    }
  }

  // ─── Family Visual ───
  function renderFamilyVisual() {
    var container = document.getElementById('familyVisual');
    if (!container) return;

    var totalDots = 186;
    var selfIndex = totalDots - 1; // pa Oracle is the latest
    var html = '';

    for (var i = 0; i < totalDots; i++) {
      var cls = 'family-dot';
      if (i === selfIndex) {
        cls += ' self';
      } else if (Math.random() > 0.6) {
        cls += ' highlight';
      }
      html += '<div class="' + cls + '" style="animation-delay: ' + (i * 8) + 'ms"></div>';
    }
    container.innerHTML = html;

    // Animate random dots periodically
    setInterval(function () {
      var dots = container.querySelectorAll('.family-dot:not(.self)');
      if (dots.length === 0) return;
      var idx = Math.floor(Math.random() * dots.length);
      dots[idx].classList.add('highlight');
      setTimeout(function () {
        dots[idx].classList.remove('highlight');
      }, 2000);
    }, 500);
  }

  // ─── Status Animation ───
  function startStatusAnimation() {
    var statusText = document.getElementById('statusText');
    if (!statusText) return;

    var states = ['Awakened', 'Observing', 'Weighing', 'Balanced'];
    var current = 0;

    setInterval(function () {
      current = (current + 1) % states.length;
      statusText.style.opacity = '0';
      setTimeout(function () {
        statusText.textContent = states[current];
        statusText.style.opacity = '1';
      }, 300);
    }, 5000);

    statusText.style.transition = 'opacity 0.3s ease';
  }

  // ─── Utils ───
  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

})();
