const fs = require('fs');
const html = fs.readFileSync('backend/templates/index.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/);
if (scriptMatch) {
    const js = scriptMatch[1];
    const lines = js.split('\n');
    // Try parsing line by line using acorn-like approach - compile progressively
    for (let i = 1; i <= lines.length; i++) {
        try {
            new Function(lines.slice(0, i).join('\n'));
        } catch (e) {
            if (e.message.includes('missing )') || e.message.includes('argument list')) {
                console.log('Syntax error near block ending at line', i);
                console.log('--- Error:', e.message);
                const start = Math.max(1, i - 5);
                for (let j = start; j <= i; j++) {
                    console.log(j + ': ' + (lines[j - 1] || ''));
                }
                break;
            }
        }
    }
    // Try alternate approach: find line of error with try each wrapped
    const vm = require('vm');
    try {
        new vm.Script(js, {displayErrors: true});
    } catch(e) {
        console.log('LINE STACK:', e.stack.split('\n').slice(0,3).join('\n'));
    }
}
