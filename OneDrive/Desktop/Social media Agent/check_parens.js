const fs = require('fs');
const code = fs.readFileSync('extracted.js', 'utf8');
const lines = code.split('\n');

console.log('=== Checking for unbalanced parentheses/brackets/braces line by line ===\n');

let globalParen = 0, globalBracket = 0, globalBrace = 0;
let issues = [];

for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    let paren = 0, bracket = 0, brace = 0;
    let inStr = null, inTemplate = false, escape = false, inComment = false, inBlockComment = false;
    
    for (let j = 0; j < line.length; j++) {
        const ch = line[j];
        const next = line[j + 1];
        
        if (escape) { escape = false; continue; }
        if (ch === '\\' && !inComment && !inBlockComment) { escape = true; continue; }
        
        if (!inStr && !inTemplate && !inComment && !inBlockComment) {
            if (ch === '/' && next === '/') { inComment = true; break; }
            if (ch === '/' && next === '*') { inBlockComment = true; j++; continue; }
        }
        if (inBlockComment) {
            if (ch === '*' && next === '/') { inBlockComment = false; j++; }
            continue;
        }
        
        if (!inBlockComment && !inComment) {
            if (!inStr && !inTemplate && ch === '`') { inTemplate = true; continue; }
            else if (inTemplate && ch === '`') { inTemplate = false; continue; }
            
            if (!inTemplate) {
                if (!inStr && (ch === '"' || ch === "'")) { inStr = ch; continue; }
                else if (inStr && ch === inStr) { inStr = null; continue; }
            }
            
            if (!inStr && !inTemplate) {
                if (ch === '(') paren++;
                if (ch === ')') paren--;
                if (ch === '[') bracket++;
                if (ch === ']') bracket--;
                if (ch === '{') brace++;
                if (ch === '}') brace--;
            }
        }
    }
    
    globalParen += paren;
    globalBracket += bracket;
    globalBrace += brace;
    
    if (paren !== 0 || bracket !== 0 || brace !== 0) {
        issues.push({
            line: i + 1,
            paren, bracket, brace,
            gParen: globalParen, gBracket: globalBracket, gBrace: globalBrace,
            text: line.substring(0, 100)
        });
    }
}

if (issues.length === 0) {
    console.log('No per-line imbalances found (might still have cross-line imbalances).');
} else {
    console.log('Lines with non-zero deltas:');
    for (const iss of issues.slice(0, 40)) {
        const tags = [];
        if (iss.paren !== 0) tags.push(`paren:${iss.paren > 0 ? '+' : ''}${iss.paren}`);
        if (iss.bracket !== 0) tags.push(`bracket:${iss.bracket > 0 ? '+' : ''}${iss.bracket}`);
        if (iss.brace !== 0) tags.push(`brace:${iss.brace > 0 ? '+' : ''}${iss.brace}`);
        console.log(`  Line ${iss.line} (${tags.join(', ')}) (cumulatives: P=${iss.gParen} Bk=${iss.gBracket} Br=${iss.gBrace}):`);
        console.log(`    ${iss.text}`);
    }
    if (issues.length > 40) console.log(`  ... and ${issues.length - 40} more`);
}

console.log('\n=== Final cumulative deltas ===');
console.log(`  Parens (): ${globalParen}`);
console.log(`  Brackets []: ${globalBracket}`);
console.log(`  Braces {}: ${globalBrace}`);

if (globalParen !== 0) {
    console.log('\n!!! PARENTHESES ARE UNBALANCED globally:', globalParen);
    
    console.log('\n=== Searching for .map() calls to check for missing close paren ===');
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const mapMatches = [...line.matchAll(/\.map\s*\(/g)];
        if (mapMatches.length > 0) {
            let count = 0;
            for (const ch of line) {
                if (ch === '(') count++;
                if (ch === ')') count--;
            }
            if (count > 0) {
                console.log(`  Potential issue at line ${i + 1}: .map() with +${count} unclosed on this line:`);
                console.log('    ' + line.substring(0, 150));
            }
        }
    }
}
