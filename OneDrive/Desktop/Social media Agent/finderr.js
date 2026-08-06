const fs = require('fs');
const html = fs.readFileSync('backend/templates/index.html', 'utf8');
// Extract last big script block
const lastScriptStart = html.lastIndexOf('<script>');
const lastScriptEnd = html.lastIndexOf('</script>');
const js = html.substring(lastScriptStart + 8, lastScriptEnd);
fs.writeFileSync('extracted.js', js);
console.log('Wrote extracted.js, lines:', js.split('\n').length);
// Now use node --check which gives proper line errors
const {execSync} = require('child_process');
try { execSync('node --check extracted.js', {stdio: 'pipe'}); console.log('No syntax errors'); }
catch(e) {
    const output = e.stderr ? e.stderr.toString() : e.toString();
    console.log(output);
    // Show referenced lines
    const m = output.match(/extracted\.js:(\d+)/);
    if (m) {
        const lineNo = parseInt(m[1]);
        const lines = js.split('\n');
        console.log('\n--- Context around line', lineNo, '---');
        for (let i = Math.max(1, lineNo-4); i <= Math.min(lines.length, lineNo+4); i++) {
            console.log(i + ': ' + lines[i-1]);
        }
    }
}
