
const $ = (s, c=document) => c.querySelector(s);
const $$ = (s, c=document) => [...c.querySelectorAll(s)];

/* Theme */
(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        $('#themeToggle').checked = true;
    }
    $('#themeToggle')?.addEventListener('change', e => {
        document.documentElement.classList.toggle('dark', e.target.checked);
        localStorage.setItem('theme', e.target.checked ? 'dark' : 'light');
        setTimeout(redrawCharts, 100);
    });
    $('#mobileMenuBtn')?.addEventListener('click', () => $('#mobileMenu').classList.toggle('hidden'));
})();

function scrollToContent() { $('#content').scrollIntoView({behavior:'smooth', block:'start'}); }
function scrollToChat() { $('#chat').scrollIntoView({behavior:'smooth', block:'start'}); setTimeout(()=>$('#chatInput').focus(), 400); }

let currentPlatform = 'linkedin';
$$('.platform-tab').forEach(btn => {
    btn.addEventListener('click', () => {
        $$('.platform-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentPlatform = btn.dataset.platform;
        $('#platformTitle').textContent = btn.textContent + ' Output';
    });
});

/* API helpers */
async function api(endpoint, data, method='POST') {
    try {
        const res = await fetch(endpoint, {
            method,
            headers: {'Content-Type':'application/json'},
            body: data ? JSON.stringify(data) : undefined
        });
        return await res.json();
    } catch(e) { return { success:false, error:String(e) }; }
}

/* Content Generation */
let lastContent = '';
async function generateContent() {
    const btn = $('#generateBtn'); const spinner = $('#genSpinner'); const label = $('#genLabel');
    btn.disabled = true; spinner.classList.remove('hidden'); label.textContent = 'Generating...';
    const r = await api('/api/content/generate', {
        platform: currentPlatform,
        topic: $('#topicInput').value,
        tone: $('#toneSelect').value,
        content_type: $('#formatSelect').value,
        audience: $('#audienceInput').value,
        keywords: $('#kwInput').value.split(',').map(s=>s.trim()).filter(Boolean)
    });
    btn.disabled = false; spinner.classList.add('hidden'); label.textContent = '✨ Generate Content';
    const out = $('#contentOutput');
    if (r.success && r.data) {
        const content = r.data.content || 'No content returned.';
        lastContent = content;
        out.style.animation='none'; out.offsetHeight; out.style.animation='fadeInUp .6s ease-out';
        out.innerHTML = '';
        const pre = document.createElement('pre');
        pre.style.cssText = 'white-space:pre-wrap;word-break:break-word;font-family:inherit;font-size:inherit';
        pre.textContent = content;
        out.appendChild(pre);
        $('#charCount').textContent = `${content.length} / ${3000}`;
        $('#mediaSuggestion').textContent = (r.data.suggested_media || '—').slice(0,40);
        $('#ctaUsed').textContent = (r.data.call_to_action || '—').slice(0,40);
    } else {
        out.textContent = '⚠️ ' + (r.error || 'Generation failed');
    }
}

function copyContent() {
    const text = lastContent || $('#contentOutput').textContent || '';
    navigator.clipboard.writeText(text).then(() => {
        const btn = event.target.closest('button') || event.currentTarget;
        const old = btn.innerHTML; btn.innerHTML = '✅ Copied!';
        setTimeout(()=> btn.innerHTML = old, 1500);
    });
}

/* Hashtags */
async function generateHashtags() {
    const out = $('#hashtagOutput');
    out.innerHTML = '<div class="flex items-center gap-2 text-sm" style="color:var(--text-muted-light)"><span class="loader-dot"></span><span class="loader-dot"></span><span class="loader-dot"></span>Optimizing mix...</div>';
    const r = await api('/api/content/hashtags', {
        content: lastContent || $('#topicInput').value,
        topic: $('#topicInput').value,
        platform: currentPlatform,
        location: $('#locInput').value || undefined,
        count: parseInt($('#tagCount').value)
    });
    if (r.success && r.data) {
        out.innerHTML = '';
        (r.data.hashtags||[]).forEach(h => {
            const chip = document.createElement('span');
            chip.className = 'tag-chip';
            const typeColor = {broad:'',niche:'rgba(139,92,246,0.12)',trending:'rgba(236,72,153,0.12)',branded:'rgba(16,185,129,0.12)',location:'rgba(6,182,212,0.12)'}[h.type];
            if (typeColor) chip.style.background = typeColor;
            chip.textContent = h.tag;
            chip.title = `${h.type} · ${(h.estimated_posts||0).toLocaleString()} posts · ${h.avg_engagement_pct}% ER`;
            out.appendChild(chip);
        });
        if (r.data.strategy) {
            const note = document.createElement('p');
            note.className = 'text-xs mt-3 w-full';
            note.style.color = 'var(--text-muted-light)';
            note.textContent = '💡 ' + r.data.strategy;
            out.appendChild(note);
        }
    }
}

/* Viral Score */
function drawFactorBreakdown(factors) {
    const container = $('#factorBreakdown');
    const weights = {hook_strength:20, emotional_resonance:20, practical_value:15, social_proof:10,
                     novelty_controversy:10, structural_quality:10, platform_fit:10, shareability:5};
    const labels = {hook_strength:'🎣 Hook Strength', emotional_resonance:'❤️ Emotional Resonance',
        practical_value:'💎 Practical Value', social_proof:'📊 Social Proof',
        novelty_controversy:'💡 Novelty / Angle', structural_quality:'📐 Structure & Flow',
        platform_fit:'📱 Platform Fit', shareability:'🔁 Shareability'};
    if (!factors) factors = Object.fromEntries(Object.keys(weights).map(k => [k, 40 + Math.random()*50]));
    container.innerHTML = Object.entries(weights).map(([k, w]) => {
        const s = typeof factors[k] === 'number' ? factors[k] : (factors[k]?.score || 60);
        const comment = factors[k]?.comment || '';
        return `<div class="mb-3">
            <div class="flex items-center justify-between text-xs mb-1.5">
                <span class="font-semibold">${labels[k]} <span class="text-[10px]" style="color:var(--text-muted-light)">(w:${w}%)</span></span>
                <span class="card-number">${Math.round(s)}%</span>
            </div>
            <div class="h-2 rounded-full overflow-hidden" style="background:var(--surface-border-light)">
                <div class="progress-bar" style="width:${s}%"></div>
            </div>
            <div class="text-[11px] mt-0.5" style="color:var(--text-muted-light)">${comment}</div>
        </div>`;
    }).join('');
}
drawFactorBreakdown();

function updateScoreRing(score) {
    const circ = 534;
    const offset = circ - (score/100) * circ;
    $('#scoreCircle').style.strokeDashoffset = offset;
    $('#scoreNumber').textContent = Math.round(score);
    let label = '❌ NEEDS WORK', color = 'rgba(239,68,68,0.15)', textColor = '#ef4444';
    if (score >= 90) { label = '🔥 VIRAL LOCKED'; color='rgba(16,185,129,0.15)'; textColor='var(--success)'; }
    else if (score >= 75) { label = '🚀 HIGH POTENTIAL'; color='rgba(139,92,246,0.15)'; textColor='#8b5cf6'; }
    else if (score >= 55) { label = '✅ GOOD'; color='rgba(99,102,241,0.15)'; textColor='var(--accent)'; }
    else if (score >= 35) { label = '⚠️ AVERAGE'; color='rgba(245,158,11,0.15)'; textColor='var(--warning)'; }
    const sl = $('#scoreLabel');
    sl.textContent = label; sl.style.background = color; sl.style.color = textColor;
}

async function runViralAnalysis() {
    const out = $('#contentOutput');
    const score = 50 + Math.random()*48;
    updateScoreRing(score);
    const breakdown = {};
    Object.keys({hook_strength:1,emotional_resonance:1,practical_value:1,social_proof:1,novelty_controversy:1,structural_quality:1,platform_fit:1,shareability:1}).forEach(k => {
        const s = 50 + Math.random()*48;
        breakdown[k] = {score: Math.round(s)};
    });
    drawFactorBreakdown(breakdown);
}

/* Trends */
async function loadTrends() {
    const grid = $('#trendsGrid');
    grid.innerHTML = Array(6).fill(0).map(() => `<div class="glass rounded-3xl p-5 animate-pulse" style="height:200px"></div>`).join('');
    const sample = [
        {topic:"Agentic AI Workflows", velocity:342, category:"Technology", growth:"SOARING", sentiment:0.82, sentiment_label:"Positive", volume:284729,
         platforms:["Twitter/X","LinkedIn"], content_ideas:["Counter-intuitive take: why most agent strategies fail","500-post analysis: 3 patterns behind 90% of success","Story: moment I realized agents weren't what I thought"]},
        {topic:"Multimodal Content Creation", velocity:267, category:"Creative", growth:"ACCELERATING", sentiment:0.76, sentiment_label:"Positive", volume:198472,
         platforms:["Instagram","TikTok"], content_ideas:["Before/after: traditional vs AI content creation","7 tools reshaping workflows this month","Hot take: quality bar just raised 10x"]},
        {topic:"Personal Brand Building", velocity:123, category:"Marketing", growth:"STABLE", sentiment:0.78, sentiment_label:"Positive", volume:589234,
         platforms:["LinkedIn","Twitter/X"], content_ideas:["3 lessons it took me 5 years to learn","Myth vs. Fact: what actually moves the needle","Framework: 5-step positioning process"]},
        {topic:"AI Ethics & Governance", velocity:178, category:"Society", growth:"ACCELERATING", sentiment:0.34, sentiment_label:"Neutral", volume:203567,
         platforms:["LinkedIn","News"], content_ideas:["Balanced take: 3 thorny tradeoffs nobody debates","2026 governance playbook","Opinion: why we're debating the wrong things"]},
        {topic:"Micro-SaaS Entrepreneurship", velocity:234, category:"Business", growth:"SOARING", sentiment:0.87, sentiment_label:"Positive", volume:134521,
         platforms:["Twitter/X","HackerNews"], content_ideas:["$0 → $10K MRR: exact 90-day playbook","7 mistakes that cost me $50K","Bootstrapped > VC-funded? Data inside"]},
        {topic:"Generative Video Production", velocity:421, category:"Creative", growth:"SOARING", sentiment:0.91, sentiment_label:"Positive", volume:167234,
         platforms:["TikTok","YouTube"], content_ideas:["I tested 8 AI video tools — clear winner inside","10 workflows anybody can copy","Future vision: 6 months from now"]}
    ];
    setTimeout(() => {
        grid.innerHTML = sample.map((t, i) => {
            const growthColors = {SOARING:'rgba(236,72,153,0.15)', ACCELERATING:'rgba(139,92,246,0.15)', STABLE:'rgba(99,102,241,0.15)', DECLINING:'rgba(245,158,11,0.15)'};
            const sentColor = t.sentiment > 0.5 ? 'var(--success)' : t.sentiment > -0.2 ? 'var(--warning)' : 'var(--danger)';
            return `<div class="glass rounded-3xl p-5 glass-hover animate-fade-up stagger-${i%8+1}">
                <div class="flex items-start justify-between mb-2">
                    <span class="badge-soft text-xs" style="background:rgba(99,102,241,0.12);color:var(--accent)">${t.category}</span>
                    <span class="badge-soft text-xs" style="background:${growthColors[t.growth]};color:#ec4899;font-weight:700">+${t.velocity}%</span>
                </div>
                <h4 class="font-bold text-lg mb-2 leading-tight">${t.topic}</h4>
                <div class="grid grid-cols-3 gap-2 text-xs mb-3">
                    <div><div class="uppercase font-semibold" style="color:var(--text-muted-light)">Volume</div><div class="card-number">${(t.volume/1000).toFixed(0)}K</div></div>
                    <div><div class="uppercase font-semibold" style="color:var(--text-muted-light)">Velocity</div><div class="card-number" style="color:#ec4899">+${t.velocity}%</div></div>
                    <div><div class="uppercase font-semibold" style="color:var(--text-muted-light)">Sentiment</div><div class="card-number" style="color:${sentColor}">${t.sentiment>0?'+':''}${t.sentiment.toFixed(2)}</div></div>
                </div>
                <div class="flex flex-wrap gap-1 mb-3">
                    ${t.platforms.map(p=>`<span class="text-[10px] px-2 py-0.5 rounded-full" style="background:var(--surface-border-light)">${p}</span>`).join('')}
                </div>
                <details class="text-xs"><summary class="font-semibold flex items-center gap-1 py-1">💡 Content angle ideas <span class="chev transition-transform">▾</span></summary>
                    <ul class="mt-2 space-y-1 pl-1" style="color:var(--text-muted-light)">
                        ${(t.content_ideas||[]).map(x=>`<li>• ${x}</li>`).join('')}
                    </ul>
                </details>
            </div>`;
        }).join('');
    }, 500);
}
loadTrends();

/* Calendar */
async function loadCalendar() {
    const body = $('#calendarBody');
    body.innerHTML = `<tr><td colspan="9" class="py-10 text-center text-sm" style="color:var(--text-muted-light)"><div class="flex items-center justify-center gap-2"><span class="loader-dot"></span><span class="loader-dot"></span><span class="loader-dot"></span>Building optimized schedule...</div></td></tr>`;
    const days = parseInt($('#calDays').value);
    const cats = {Educational:"#6366f1", Promotional:"#ec4899", Engaging:"#8b5cf6", Community:"#10b981", "Behind-the-Scenes":"#f59e0b"};
    const now = new Date();
    const rows = [];
    const platforms = {twitter:"X/Twitter", linkedin:"LinkedIn", instagram:"Instagram", facebook:"Facebook"};
    for (let d=0; d<days; d++) {
        const date = new Date(now); date.setDate(now.getDate()+d);
        const dayName = date.toLocaleDateString('en-US', {weekday:'long'});
        const dow = date.getDay();
        const times = {twitter:["09:00","15:00","21:00"], linkedin:["08:00","12:00","17:00"], instagram:["11:00","19:00"], facebook:["13:00","19:00"]};
        Object.entries(times).forEach(([p, arr]) => {
            if (dow === 0 && p === 'linkedin') return;
            const count = (d + p.length) % 2 === 0 ? Math.min(arr.length,2) : 1;
            arr.slice(0, count).forEach(time => {
                const cat = Object.keys(cats)[(d + Object.keys(platforms).indexOf(p)+ Math.floor(time.split(':')[0]/3)) % Object.keys(cats).length];
                const topics = [
                    "Industry trend analysis + counter-intuitive data",
                    "3 lessons from failures nobody shares",
                    "Customer success story w/ specific numbers",
                    "Quick 60-second productivity win",
                    "Myth vs. Fact: Debunking common beliefs",
                    "Update: Exactly why we built this",
                    "Poll + discussion: Your perspective?",
                    "5-step framework for results"
                ];
                const fmts = ["Text Post","Carousel","Short Video","Image","Thread","Story"];
                rows.push({
                    date: date.toISOString().slice(0,10),
                    dayName, time, platform: p, platformName: platforms[p],
                    topic: topics[(d*3 + Object.values(platforms).indexOf(platforms[p])) % topics.length],
                    fmt: fmts[(d*2 + Math.floor(time.split(':')[0]/4)) % fmts.length],
                    category: cat,
                    pred: Math.round(55 + ((d*7) % 40) + Math.random()*8),
                    status: ["Draft","Scheduled","Needs Approval"][(d*3) % 3]
                });
            });
        });
    }
    rows.sort((a,b) => (a.date+a.time).localeCompare(b.date+b.time));
    setTimeout(() => {
        body.innerHTML = rows.slice(0, 60).map(r => {
            const statusColors = {Draft:"#94a3b8", Scheduled:"var(--accent)", "Needs Approval":"var(--warning)"};
            return `<tr>
                <td class="py-3 px-4 font-semibold text-sm">${r.date}</td>
                <td class="py-3 px-4">${r.dayName}</td>
                <td class="py-3 px-4 font-mono text-sm">${r.time}</td>
                <td class="py-3 px-4">
                    <span class="badge-soft text-xs" style="background:rgba(99,102,241,0.1);color:var(--accent)">${r.platformName}</span>
                </td>
                <td class="py-3 px-4 max-w-[300px] truncate" title="${r.topic}">${r.topic}</td>
                <td class="py-3 px-4 text-xs">${r.fmt}</td>
                <td class="py-3 px-4"><span class="badge-soft text-[10px]" style="background:${cats[r.category]}22;color:${cats[r.category]}">${r.category}</span></td>
                <td class="py-3 px-4 text-right font-bold card-number" style="color:${r.pred>80?'var(--success)':r.pred>65?'var(--accent)':'var(--warning)'}">${r.pred}%</td>
                <td class="py-3 px-4"><span class="badge-soft text-[10px]" style="background:${statusColors[r.status]}22;color:${statusColors[r.status]}">${r.status}</span></td>
            </tr>`;
        }).join('');
        if (rows.length > 60) {
            body.innerHTML += `<tr><td colspan="9" class="py-4 text-center text-xs" style="color:var(--text-muted-light)">+ ${rows.length-60} more scheduled items</td></tr>`;
        }
    }, 600);
}
loadCalendar();

/* Competitors */
async function loadCompetitors() {
    const list = $('#rankingList');
    list.innerHTML = `<div class="text-sm py-8 text-center" style="color:var(--text-muted-light)"><span class="loader-dot"></span><span class="loader-dot"></span><span class="loader-dot"></span></div>`;
    const ranking = [
        {name:"IndustryLeaderCo", score:91, tier:"LEADER", color:"#6366f1"},
        {name:"YOUR BRAND", score:77, tier:"CHALLENGER", color:"#10b981", us:true},
        {name:"CompetitorBrandA", score:72, tier:"CONTENDER", color:"#8b5cf6"},
        {name:"DirectRivalX", score:63, tier:"CONTENDER", color:"#f59e0b"},
        {name:"EmergingNewCo", score:54, tier:"LAGGARD", color:"#94a3b8"}
    ];
    setTimeout(() => {
        list.innerHTML = ranking.map((r,i) => `
            <div class="rounded-2xl p-3 glass-hover border flex items-center gap-3" style="border-color:var(--surface-border-light)${r.us?';background:rgba(16,185,129,0.07)':''}">
                <div class="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm" style="background:${r.color}22;color:${r.color}">${i+1}</div>
                <div class="flex-1 min-w-0">
                    <div class="font-semibold text-sm truncate">${r.name} ${r.us?'<span class="badge-soft ml-1 text-[10px]" style="background:rgba(16,185,129,0.2);color:var(--success)">YOU</span>':''}</div>
                    <span class="badge-soft text-[10px]" style="background:${r.color}22;color:${r.color}">${r.tier}</span>
                </div>
                <div class="text-right">
                    <div class="card-number text-2xl" style="color:${r.color}">${r.score}</div>
                    <div class="text-[10px]" style="color:var(--text-muted-light)">/ 100</div>
                </div>
            </div>`).join('');
    }, 500);
}
loadCompetitors();

/* Sentiment */
function drawSentimentGauge() {
    const c = $('#sentimentGauge'); if (!c) return;
    const ctx = c.getContext('2d');
    const isDark = document.documentElement.classList.contains('dark');
    const w = c.width, h = c.height;
    ctx.clearRect(0,0,w,h);
    const cx = w/2, cy = h-4, r = 100;
    const grd = ctx.createLinearGradient(0,0,w,0);
    grd.addColorStop(0,'#ef4444'); grd.addColorStop(0.5,'#fbbf24'); grd.addColorStop(1,'#10b981');
    ctx.lineWidth = 18; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.strokeStyle = isDark?'rgba(255,255,255,0.08)':'rgba(15,23,42,0.08)';
    ctx.arc(cx,cy,r,Math.PI, 2*Math.PI); ctx.stroke();
    ctx.beginPath(); ctx.strokeStyle = grd;
    const pos = 0.68;
    ctx.arc(cx,cy,r,Math.PI, Math.PI + Math.PI*pos); ctx.stroke();
}

async function runSentiment() {
    const data = {sentiment_score:0.55 + Math.random()*0.35,
        distribution:{very_positive_pct:32+Math.random()*10,positive_pct:22+Math.random()*10,neutral_pct:18+Math.random()*10,negative_pct:6+Math.random()*10,very_negative_pct:3+Math.random()*6}};
    const total = Object.values(data.distribution).reduce((a,b)=>a+b,1);
    const scale = 100/total;
    Object.keys(data.distribution).forEach(k => data.distribution[k] *= scale);
    const s = data.sentiment_score;
    $('#sentScore').textContent = (s>0?'+':'') + s.toFixed(2);
    const sl = $('#sentLabel');
    if (s > 0.5) { sl.style.cssText='background:rgba(16,185,129,0.15);color:var(--success)'; sl.textContent='Very Positive'; }
    else if (s > 0.2) { sl.style.cssText='background:rgba(52,211,153,0.15);color:#34d399'; sl.textContent='Positive'; }
    else if (s > -0.2) { sl.style.cssText='background:rgba(148,163,184,0.15);color:var(--text-muted-light)'; sl.textContent='Neutral'; }
    else if (s > -0.5) { sl.style.cssText='background:rgba(251,191,36,0.15);color:var(--warning)'; sl.textContent='Negative'; }
    else { sl.style.cssText='background:rgba(239,68,68,0.15);color:var(--danger)'; sl.textContent='Very Negative'; }
    [['vp',38,'vpBar','vpPct'],['p',27,'pBar','pPct'],['n',20,'nBar','nPct'],['ng',10,'ngBar','ngPct'],['vn',5,'vnBar','vnPct']].forEach(([k,_,bid,pid]) => {
        const key = {vp:'very_positive_pct',p:'positive_pct',n:'neutral_pct',ng:'negative_pct',vn:'very_negative_pct'}[k];
        const v = data.distribution[key].toFixed(1);
        $('#'+bid).style.width = v + '%';
        $('#'+pid).textContent = v + '%';
    });
    drawSentimentGauge();
    loadTopics();
}

function loadTopics() {
    const items = [
        {name:"Product & Features", mentions:68, sentiment:0.78, label:"Positive", color:"var(--success)"},
        {name:"Customer Support", mentions:42, sentiment:0.65, label:"Positive", color:"var(--success)"},
        {name:"Pricing & Value", mentions:34, sentiment:0.12, label:"Neutral", color:"var(--warning)"},
        {name:"Ease of Use", mentions:28, sentiment:0.71, label:"Positive", color:"#34d399"},
        {name:"Updates & Roadmap", mentions:24, sentiment:0.24, label:"Neutral", color:"var(--accent)"}
    ];
    $('#topicsList').innerHTML = items.map(t => `
        <details class="rounded-xl border p-3" style="border-color:var(--surface-border-light)">
            <summary class="flex items-center justify-between gap-4">
                <div class="flex items-center gap-3 min-w-0 flex-1">
                    <div class="w-9 h-9 rounded-lg flex items-center justify-center font-bold text-xs" style="background:${t.color}22;color:${t.color}">${t.mentions}</div>
                    <div class="min-w-0">
                        <div class="font-semibold text-sm truncate">${t.name}</div>
                        <div class="text-[11px]" style="color:var(--text-muted-light)">${t.mentions} mentions · Avg. sentiment
                            <span class="font-bold" style="color:${t.color}">${t.sentiment>0?'+':''}${t.sentiment.toFixed(2)}</span>
                        </div>
                    </div>
                </div>
                <span class="chev transition-transform text-xs" style="color:var(--text-muted-light)">▾</span>
            </summary>
            <div class="mt-3 text-xs pl-12 space-y-1" style="color:var(--text-muted-light)">
                <div><span class="font-semibold" style="color:var(--text-light)">Top keywords:</span> quality, experience, features, interface, performance</div>
                <div><span class="font-semibold" style="color:var(--text-light)">Action:</span> Leverage strong Product sentiment in next campaign creative</div>
            </div>
        </details>
    `).join('');
}
loadTopics();

/* Charts */
let charts = {};
function chartColors() {
    const dark = document.documentElement.classList.contains('dark');
    return {
        text: dark ? '#94a3b8' : '#64748b',
        grid: dark ? 'rgba(255,255,255,0.05)' : 'rgba(15,23,42,0.06)',
        surface: dark ? '#111827' : '#ffffff'
    };
}
function chartFont() { return {family:"'Inter', sans-serif", size:11, weight:500}; }
Chart.defaults.font.family = "'Inter', sans-serif";

function redrawCharts() {
    Object.values(charts).forEach(c => { try { c.destroy(); } catch(e){} });
    charts = {};
    drawAllCharts();
}

function drawAllCharts() {
    const col = chartColors();
    const commonOpts = {
        responsive:true, maintainAspectRatio:true, plugins:{legend:{display:false}},
        scales:{
            x:{ticks:{color:col.text,font:chartFont()}, grid:{color:col.grid, drawBorder:false}, border:{display:false}},
            y:{ticks:{color:col.text,font:chartFont()}, grid:{color:col.grid, drawBorder:false}, border:{display:false}}
        }
    };

    // Hero
    const hctx = $('#heroChart')?.getContext('2d');
    if (hctx && !charts.hero) {
        const days = 14; const lbls = Array.from({length:days}, (_,i)=>`${i+1}`);
        charts.hero = new Chart(hctx, {type:'line', data:{labels:lbls, datasets:[
            {label:'Engagements', data:Array.from({length:days}, ()=> Math.round(1500 + Math.random()*3500 + 150*Math.sin(Math.random()*10))),
             borderColor:'#8b5cf6', backgroundColor:'rgba(139,92,246,0.15)', tension:.4, fill:true, pointRadius:0, borderWidth:2.5}
        ]}, options:{...commonOpts, plugins:{legend:{display:false}}, scales:{x:{display:false},y:{display:false}}, elements:{}}});
    }

    // Main Reach + Engagement
    const mctx = $('#mainChart')?.getContext('2d');
    if (mctx && !charts.main) {
        const days = 30; const labels = Array.from({length:days},(_,i)=> `Day ${i+1}`);
        const reach = labels.map((_,i)=> 30000 + Math.round(Math.abs(Math.sin(i/3)*45000) + Math.random()*25000));
        const eng = reach.map(v => Math.round(v * (0.035 + Math.random()*0.04)));
        charts.main = new Chart(mctx, {type:'line', data:{labels, datasets:[
            {label:'Reach', data:reach, borderColor:'#6366f1', backgroundColor:(ctx)=>{
                const g = ctx.chart.ctx.createLinearGradient(0,0,0,250);
                g.addColorStop(0,'rgba(99,102,241,0.3)'); g.addColorStop(1,'rgba(99,102,241,0)'); return g;
            }, yAxisID:'y', tension:.4, fill:true, pointRadius:0, borderWidth:2.5},
            {label:'Engagements', data:eng, borderColor:'#ec4899', backgroundColor:(ctx)=>{
                const g = ctx.chart.ctx.createLinearGradient(0,0,0,250);
                g.addColorStop(0,'rgba(236,72,153,0.25)'); g.addColorStop(1,'rgba(236,72,153,0)'); return g;
            }, yAxisID:'y1', tension:.4, fill:true, pointRadius:0, borderWidth:2.5}
        ]}, options:{...commonOpts, plugins:{legend:{display:false}},
            scales:{
                x:{ticks:{color:col.text, font:chartFont(), maxTicksLimit:8}, grid:{color:col.grid, drawBorder:false}, border:{display:false}},
                y:{position:'left', ticks:{color:'#6366f1',font:chartFont()}, grid:{color:col.grid, drawBorder:false}, border:{display:false}},
                y1:{position:'right', ticks:{color:'#ec4899',font:chartFont()}, grid:{display:false}, border:{display:false}}
            }
        }});
    }

    // Platform Radar
    const rctx = $('#platformRadar')?.getContext('2d');
    if (rctx && !charts.radar) {
        charts.radar = new Chart(rctx, {type:'radar', data:{
            labels:['Reach','Engagement','Growth','Consistency','Content Quality','Community'],
            datasets:[
                {label:'LinkedIn', data:[78,88,72,65,82,60], borderColor:'#0A66C2', backgroundColor:'rgba(10,102,194,0.15)', borderWidth:2, pointRadius:2},
                {label:'Instagram', data:[92,82,68,70,78,88], borderColor:'#ec4899', backgroundColor:'rgba(236,72,153,0.15)', borderWidth:2, pointRadius:2},
                {label:'Twitter/X', data:[72,65,80,85,70,55], borderColor:'#6366f1', backgroundColor:'rgba(99,102,241,0.15)', borderWidth:2, pointRadius:2}
            ]
        }, options:{
            responsive:true, plugins:{legend:{position:'bottom', labels:{color:col.text, font:{...chartFont(), size:10}, boxWidth:10, padding:10}}},
            scales:{r:{
                angleLines:{color:col.grid}, grid:{color:col.grid},
                pointLabels:{color:col.text, font:chartFont()},
                ticks:{color:col.text, backdropColor:'transparent', font:chartFont()},
                suggestedMin:0, suggestedMax:100
            }}
        }});
    }

    // Format bar
    const fctx = $('#formatChart')?.getContext('2d');
    if (fctx && !charts.format) {
        charts.format = new Chart(fctx, {type:'bar', data:{
            labels:['Short Video','Carousel','Static Image','Text/Link','Live/Stories'],
            datasets:[{label:'Engagement %', data:[6.8,5.4,3.2,2.1,4.5], borderRadius:10, borderSkipped:false,
                backgroundColor:['#ec4899','#8b5cf6','#6366f1','#06b6d4','#10b981'].map(c=>c+'')}]
        }, options:{
            responsive:true, indexAxis:'y', plugins:{legend:{display:false}},
            scales:{
                x:{ticks:{color:col.text,font:chartFont()}, grid:{color:col.grid}, border:{display:false}},
                y:{ticks:{color:col.text,font:chartFont()}, grid:{display:false}, border:{display:false}}
            }
        }});
    }

    // Growth
    const gctx = $('#growthChart')?.getContext('2d');
    if (gctx && !charts.growth) {
        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug'];
        const base = 80000;
        let val = base;
        const data = months.map(() => { val = Math.round(val * (1.05 + Math.random()*0.07)); return val; });
        charts.growth = new Chart(gctx, {type:'bar', data:{labels:months, datasets:[
            {type:'bar', label:'Followers', data, backgroundColor:(ctx)=>{
                const g = ctx.chart.ctx.createLinearGradient(0,0,0,250);
                g.addColorStop(0,'#6366f1'); g.addColorStop(1,'#8b5cf6'); return g;
            }, borderRadius:8, borderSkipped:false, order:2},
            {type:'line', label:'Growth trend', data, borderColor:'#ec4899', backgroundColor:'transparent', tension:.35, borderWidth:2.5, pointRadius:3, pointBackgroundColor:'#ec4899', order:1}
        ]}, options:{...commonOpts, plugins:{legend:{display:false}}}});
    }

    // Competitor
    const cctx = $('#competitorChart')?.getContext('2d');
    if (cctx && !charts.comp) {
        charts.comp = new Chart(cctx, {type:'bar', data:{
            labels:['YOUR BRAND','IndustryLeaderCo','CompetitorA','DirectRivalX','EmergingNewCo'],
            datasets:[
                {label:'Followers (K)', data:[173,412,118,95,38], backgroundColor:'rgba(99,102,241,0.8)', borderRadius:6, yAxisID:'y'},
                {label:'ER %', data:[5.8,4.2,5.1,3.4,6.7], backgroundColor:'rgba(139,92,246,0.8)', borderRadius:6, yAxisID:'y1'},
                {label:'Posts/wk', data:[12,19,14,8,22], backgroundColor:'rgba(16,185,129,0.8)', borderRadius:6, yAxisID:'y2'}
            ]
        }, options:{
            responsive:true, plugins:{legend:{position:'bottom', labels:{color:col.text, font:chartFont(), boxWidth:12}}},
            scales:{
                x:{ticks:{color:col.text,font:chartFont()}, grid:{display:false}, border:{display:false}},
                y:{position:'left', ticks:{color:'#6366f1',font:chartFont()}, grid:{color:col.grid}, border:{display:false}, title:{display:true,text:'Followers K',color:'#6366f1',font:chartFont()}},
                y1:{position:'right', ticks:{color:'#8b5cf6',font:chartFont()}, grid:{display:false}, border:{display:false}, title:{display:true,text:'ER %',color:'#8b5cf6',font:chartFont()}},
                y2:{display:false}
            }
        }});
    }

    // Emotions barh
    const ectx = $('#emotionChart')?.getContext('2d');
    if (ectx && !charts.emotion) {
        charts.emotion = new Chart(ectx, {type:'bar', data:{
            labels:['Joy','Trust','Excitement','Hope','Gratitude','Neutral','Frustration','Disappointment','Confusion','Skepticism'],
            datasets:[{label:'Score', data:[0.52,0.48,0.44,0.39,0.32,0.35,0.15,0.13,0.12,0.16], borderRadius:8, borderSkipped:false,
                backgroundColor:['#10b981','#6366f1','#8b5cf6','#ec4899','#f59e0b','#94a3b8','#ef4444','#f97316','#64748b','#a855f7']}]
        }, options:{
            responsive:true, indexAxis:'y', plugins:{legend:{display:false}},
            scales:{
                x:{ticks:{color:col.text,font:chartFont()}, grid:{color:col.grid}, border:{display:false}, max:0.7},
                y:{ticks:{color:col.text,font:chartFont()}, grid:{display:false}, border:{display:false}}
            }
        }});
    }

    // Hours grid
    const hg = $('#hoursGrid');
    if (hg && hg.children.length === 0) {
        const hours = [{t:"08:00",v:85},{t:"09:00",v:92},{t:"10:00",v:98},{t:"11:00",v:88},
                       {t:"12:00",v:78},{t:"13:00",v:82},{t:"14:00",v:90},{t:"15:00",v:95},
                       {t:"17:00",v:84},{t:"18:00",v:76},{t:"19:00",v:72},{t:"21:00",v:68}];
        hg.innerHTML = hours.sort((a,b)=>b.v-a.v).map(h => {
            const tier = h.v > 90 ? '🏆 PEAK' : h.v > 80 ? '✅ GOOD' : '⚠️ OK';
            const color = h.v > 90 ? 'var(--success)' : h.v > 80 ? 'var(--accent)' : 'var(--warning)';
            return `<div class="rounded-xl p-2 text-center" style="background:rgba(99,102,241,0.06)">
                <div class="font-mono text-xs font-bold">${h.t}</div>
                <div class="card-number text-xl my-1" style="color:${color}">${h.v}</div>
                <div class="text-[9px] font-semibold" style="color:${color}">${tier}</div>
            </div>`;
        }).join('');
    }

    // Insights list
    const il = $('#insightsList');
    if (il && il.children.length === 0) {
        const ins = [
            {p:"HIGH", title:"Short-form video is driving disproportionate results", detail:"ER on Reels/Shorts 3.2x vs. text posts. Current allocation 35% → increase to 45%.", impact:"📈 +18% total engagements in 30 days", color:"var(--success)"},
            {p:"HIGH", title:"CTR gap on link-in-bio calls to action", detail:"Clicks 38% below average. Test explicit link in caption first sentence vs. end placement.", impact:"🔗 +12% referral traffic", color:"var(--accent)"},
            {p:"MEDIUM", title:"Sunday posts show hidden save value on Instagram", detail:"+22% save rate on Sunday. Currently 8% of content on weekends. Add Sunday carousel.", impact:"💾 Improved algorithm favorability", color:"#8b5cf6"},
            {p:"HIGH", title:"Viral post pattern: personal story + numbered framework", detail:"Top 5 posts all include personal anecdote + 3-5 step list. 88% replication score.", impact:"🎯 2.1x posts reaching >100K impressions", color:"#ec4899"}
        ];
        il.innerHTML = ins.map(x => `
            <div class="rounded-2xl p-4 glass-hover border" style="border-color:var(--surface-border-light)">
                <div class="flex items-center justify-between mb-2">
                    <span class="badge-soft text-[10px]" style="background:${x.color}22;color:${x.color}; font-weight:700">${x.p} PRIORITY</span>
                    <div class="text-xs font-bold" style="color:${x.color}">${Math.round(80+Math.random()*17)}% confident</div>
                </div>
                <h5 class="font-bold mb-1 text-sm">${x.title}</h5>
                <p class="text-xs mb-2" style="color:var(--text-muted-light)">${x.detail}</p>
                <div class="badge-soft text-[10px]" style="background:rgba(99,102,241,0.1); color:var(--accent)">${x.impact}</div>
            </div>`).join('');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    drawAllCharts();
    drawSentimentGauge();
});

/* Chat */
function autoResize(el) { el.style.height = 'auto'; el.style.height = (el.scrollHeight) + 'px'; if (el.value.trim() === '') el.style.height = 'auto'; }

function appendUser(text) {
    const wrap = document.createElement('div');
    wrap.className = 'flex gap-3 items-start justify-end animate-slide-in';
    wrap.innerHTML = `
        <div class="chat-bubble-user p-4 max-w-[85%] text-sm whitespace-pre-wrap">${escapeHtml(text)}</div>
        <div class="w-8 h-8 rounded-xl flex items-center justify-center text-xs font-bold flex-shrink-0 mt-1 glass border">You</div>`;
    $('#chatMessages').appendChild(wrap);
    scrollChat();
}
function appendAI(text, toolName) {
    const wrap = document.createElement('div');
    wrap.className = 'flex gap-3 items-start animate-fade-up';
    wrap.innerHTML = `
        <div class="w-8 h-8 rounded-xl gradient-btn flex items-center justify-center text-xs font-bold flex-shrink-0 mt-1">AI</div>
        <div class="chat-bubble-ai p-4 max-w-[85%] text-sm whitespace-pre-wrap">
            ${toolName ? `<div class="badge-soft mb-2 text-[10px]" style="background:rgba(99,102,241,0.15);color:var(--accent);font-weight:700">🛠️ Used: ${toolName}</div>` : ''}
            ${formatAI(text)}
        </div>`;
    $('#chatMessages').appendChild(wrap);
    scrollChat();
}
function appendTyping() {
    const wrap = document.createElement('div');
    wrap.id = 'typingIndicator';
    wrap.className = 'flex gap-3 items-start';
    wrap.innerHTML = `
        <div class="w-8 h-8 rounded-xl gradient-btn flex items-center justify-center text-xs font-bold flex-shrink-0 mt-1">AI</div>
        <div class="chat-bubble-ai p-4 flex items-center gap-2 text-xs" style="color:var(--text-muted-light)">
            <span class="loader-dot"></span><span class="loader-dot"></span><span class="loader-dot"></span>
            <span class="ml-1">Agent thinking & routing...</span>
        </div>`;
    $('#chatMessages').appendChild(wrap);
    scrollChat();
}
function removeTyping() { $('#typingIndicator')?.remove(); }
function scrollChat() { const el = $('#chatMessages'); el.scrollTop = el.scrollHeight; }
function escapeHtml(s) { return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }
function formatAI(s) {
    s = escapeHtml(s);
    s = s.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/\n/g, '<br>');
    return s;
}

function quickAsk(q) { $('#chatInput').value = q; sendChat(new Event('submit')); }

function clearChat() {
    const el = $('#chatMessages');
    el.innerHTML = `<div class="flex gap-3 items-start animate-fade-up">
        <div class="w-8 h-8 rounded-xl gradient-btn flex items-center justify-center text-xs flex-shrink-0 mt-1">AI</div>
        <div class="chat-bubble-ai p-4 max-w-[85%] text-sm">Chat cleared. What would you like help with?</div>
    </div>`;
}

async function sendChat(ev) {
    ev.preventDefault();
    const input = $('#chatInput');
    const text = input.value.trim();
    if (!text) return;
    appendUser(text);
    input.value = ''; autoResize(input);
    appendTyping();
    const r = await api('/api/chat/message', {messages:[{role:'user',content:text}]});
    removeTyping();
    if (r.success && r.data) {
        appendAI(r.data.assistant_message, r.data.tool_used);
        if (r.data.tool_used) {
            $('#agentName').textContent = `Just routed through ${r.data.tool_used}`;
            setTimeout(() => $('#agentName').textContent = '6 specialist agents · IBM Granite online', 3000);
        }
    } else {
        appendAI('Sorry, I ran into an issue. Please try again.', null);
    }
}

/* Smooth-scroll active nav */
const navLinks = $$('.nav-item');
const sections = ['dashboard','content','trends','calendar','competitor','sentiment','analytics','chat']
    .map(id => document.getElementById(id)).filter(Boolean);
window.addEventListener('scroll', () => {
    let cur = sections[0];
    sections.forEach(s => {
        if (s.getBoundingClientRect().top <= 120) cur = s;
    });
    navLinks.forEach(a => {
        const href = a.getAttribute('href') || '';
        a.classList.toggle('active', href === '#' + cur.id);
    });
}, {passive:true});

