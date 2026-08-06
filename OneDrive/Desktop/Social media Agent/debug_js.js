const fs = require('fs');
const code = fs.readFileSync('extracted.js', 'utf8');
const lines = code.split('\n');

console.log('=== Checking for invisible characters around line 429 ===');
for (let i = 427; i <= 431; i++) {
    const line = lines[i];
    console.log('Line ' + (i + 1) + ':');
    console.log('  Text:', JSON.stringify(line));
    let hasInvisible = false;
    for (let j = 0; j < line.length; j++) {
        const cc = line.charCodeAt(j);
        if (cc < 32 || cc > 126 || cc === 8203 || cc === 65279 || cc === 8232 || cc === 8233) {
            console.log('  ** Invisible char at pos', j, 'code:', cc, 'char:', JSON.stringify(line[j]));
            hasInvisible = true;
        }
    }
    if (!hasInvisible) console.log('  (no invisible chars)');
}

console.log('\n=== Testing chunks ===');

const testChunk = (startLine, endLine, label) => {
    const chunk = lines.slice(startLine - 1, endLine).join('\n');
    try {
        new Function(chunk);
        console.log(`  ${label} (lines ${startLine}-${endLine}): OK`);
        return true;
    } catch (e) {
        console.log(`  ${label} (lines ${startLine}-${endLine}): FAIL - ${e.message}`);
        return false;
    }
};

testChunk(405, 423, 'Hero section');
testChunk(425, 447, 'Main chart section');
testChunk(427, 431, 'Lines 428-431 only');
testChunk(405, 403 + 1, 'commonOpts');

console.log('\n=== Smaller test of the exact problematic area ===');
const tinyStub = `
let charts = {};
const $ = () => ({ getContext: () => ({}), classList: { toggle() {} } });
const Chart = function() {};
Chart.defaults = { font: {} };
function chartColors() { return {text:'',grid:'',surface:''}; }
function chartFont() { return {}; }
const col = chartColors();
const commonOpts = { responsive:true, scales:{ x:{}, y:{} }, plugins:{ legend:{} } };
`;

const mainChartCode = lines.slice(425, 447).join('\n');
try {
    new Function(tinyStub + mainChartCode);
    console.log('  Main chart with stubs: OK');
} catch (e) {
    console.log('  Main chart with stubs FAIL:');
    console.log('  Error:', e.message);
    
    const m = e.message.match(/:(\d+)/);
    if (m) {
        const errLineInChunk = parseInt(m[1]);
        const stubLines = tinyStub.split('\n').length;
        const realLine = 425 + (errLineInChunk - stubLines) - 1;
        console.log('  Error maps to extracted.js line approximately:', realLine);
        for (let j = Math.max(425, realLine - 3); j <= Math.min(447, realLine + 3); j++) {
            console.log('    ' + j + ': ' + (lines[j - 1] || ''));
        }
    }
}
