const fs = require('fs');
const vm = require('vm');

let code = fs.readFileSync('extracted.js', 'utf8');
let attempt = 0;
const maxAttempts = 20;
const fixes = [];

while (attempt < maxAttempts) {
    attempt++;
    try {
        new vm.Script(code, { displayErrors: false });
        console.log(`\n✅ All syntax errors fixed! (${attempt - 1} total fixes applied)`);
        break;
    } catch (e) {
        const m = e.stack.match(/evalmachine\.<anonymous>:(\d+)/);
        if (!m) {
            console.log('Could not parse error:', e.message);
            console.log('Stack:', e.stack.split('\n').slice(0, 3).join('\n'));
            break;
        }
        const lineNo = parseInt(m[1]);
        const lines = code.split('\n');
        const badLine = lines[lineNo - 1] || '';
        
        console.log(`\n--- Fix attempt ${attempt} ---`);
        console.log(`Error at line ${lineNo}: ${e.message}`);
        console.log(`Line ${lineNo} content: ${JSON.stringify(badLine.substring(0, 150))}`);
        
        let fixed = false;
        
        if (badLine.includes('.map(') || badLine.includes('.forEach(') || badLine.includes('.filter(') || 
            badLine.includes('Array.from(') || badLine.includes('api(') || badLine.includes('fetch(') ||
            badLine.includes('new Chart(') || badLine.includes('new Function(') ||
            badLine.match(/\b\w+\([^)]*=>/)) {
            
            let opens = 0, closes = 0;
            for (const ch of badLine) {
                if (ch === '(') opens++;
                if (ch === ')') closes++;
            }
            
            const diff = opens - closes;
            if (diff > 0) {
                console.log(`  -> Unbalanced parens: ${opens}( vs ${closes}) -> diff +${diff}`);
                
                const newLine = badLine.replace(/;?\s*$/, ')'.repeat(diff) + ';');
                lines[lineNo - 1] = newLine;
                code = lines.join('\n');
                fixes.push({ line: lineNo, added: diff, old: badLine.substring(0, 100), new: newLine.substring(0, 100) });
                console.log(`  -> Added ${diff} closing paren(s). New line end: ...${newLine.substring(Math.max(0, newLine.length - 60))}`);
                fixed = true;
            } else {
                console.log(`  -> Parens balanced on this line (${opens} vs ${closes}). Checking for other issues...`);
            }
        }
        
        if (!fixed) {
            if (badLine.includes('...')) {
                console.log('  -> Contains spread operator. Node --check should support this. Trying alternate approach.');
            }
            console.log('  -> Context around error:');
            for (let j = Math.max(0, lineNo - 5); j <= Math.min(lines.length, lineNo + 3); j++) {
                console.log(`    ${j + 1}: ${lines[j] || ''}`);
            }
            
            if (e.message.includes('Unexpected token')) {
                const tokMatch = e.message.match(/Unexpected token\s+'?([^'"\s]+)'?/);
                if (tokMatch) {
                    const unexpected = tokMatch[1];
                    console.log(`  -> Trying to insert before unexpected token: ${unexpected}`);
                    const idx = badLine.indexOf(unexpected);
                    if (idx > 0) {
                        const before = badLine.substring(0, idx);
                        const after = badLine.substring(idx);
                        let opens = 0, closes = 0;
                        for (const ch of before) {
                            if (ch === '(') opens++;
                            if (ch === ')') closes++;
                        }
                        const diff = opens - closes;
                        if (diff > 0) {
                            const newLine = before + ')'.repeat(diff) + after;
                            lines[lineNo - 1] = newLine;
                            code = lines.join('\n');
                            fixes.push({ line: lineNo, added: diff, location: `before '${unexpected}'` });
                            console.log(`  -> Inserted ${diff} paren(s) before unexpected token.`);
                            fixed = true;
                        }
                    }
                }
            }
        }
        
        if (!fixed) {
            console.log('  ❌ Could not auto-fix. Stopping.');
            break;
        }
    }
}

if (fixes.length > 0) {
    console.log('\n=== Summary of fixes ===');
    fixes.forEach((f, i) => console.log(`  Fix ${i + 1}: Line ${f.line} - added ${f.added} paren(s)`));
    fs.writeFileSync('extracted_fixed.js', code);
    console.log('\nFixed JavaScript written to extracted_fixed.js');
} else {
    console.log('No fixes needed.');
}
