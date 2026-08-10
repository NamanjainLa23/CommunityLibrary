// Lightweight ISBN formatter with heuristic hyphenation for common groups.
// This is a best-effort client-side formatter. For perfect hyphenation use an ISBN range-aware library.

export function normalizeIsbn(isbn){
  if(!isbn) return '';
  return String(isbn).toUpperCase().replace(/[^0-9X]/g,'');
}

export function formatIsbn(isbn){
  const s = normalizeIsbn(isbn);
  if(!s) return '';

  // ISBN-13
  if(s.length===13){
    // common case: 978 or 979 prefix
    const prefix = s.slice(0,3);
    const rest = s.slice(3,12);
    const check = s.slice(12);
    // heuristic: if registration group is 0 or 1 (English), split as 3-1-3-5-1
    const group = s.charAt(3);
    if(prefix === '978' || prefix === '979'){
      if(group === '0' || group === '1'){
        const g = s.slice(3,4);
        const registrant = s.slice(4,7);
        const publication = s.slice(7,12);
        return `${prefix}-${g}-${registrant}-${publication}-${check}`;
      }
      // fallback split: 3-2-4-3-1
      const g2 = s.slice(3,5);
      const reg2 = s.slice(5,9);
      const pub2 = s.slice(9,12);
      return `${prefix}-${g2}-${reg2}-${pub2}-${check}`;
    }
    return s; // unknown prefix
  }

  // ISBN-10 heuristic: group 0/1 common split 1-3-5-1
  if(s.length===10){
    const group = s.charAt(0);
    if(group === '0' || group === '1'){
      const g = s.slice(0,1);
      const registrant = s.slice(1,4);
      const publication = s.slice(4,9);
      const check = s.slice(9);
      return `${g}-${registrant}-${publication}-${check}`;
    }
    // fallback simple split
    return `${s.slice(0,2)}-${s.slice(2,5)}-${s.slice(5,9)}-${s.slice(9)}`;
  }

  return isbn;
}

export function isValidIsbn(isbn){
  const s = normalizeIsbn(isbn);
  if(!s) return false;
  if(s.length===13){
    const digits = s.split('').map(c=>parseInt(c,10));
    if(digits.some(d=>Number.isNaN(d))) return false;
    const sum = digits.slice(0,12).reduce((acc,d,i)=>(i%2===0?acc+d:acc+3*d),0);
    const check = (10 - (sum % 10)) % 10;
    return check === digits[12];
  }
  if(s.length===10){
    const base = s.slice(0,9).split('').map(c=>parseInt(c,10));
    if(base.some(d=>Number.isNaN(d))) return false;
    const sum = base.reduce((acc,d,i)=>acc + d*(10-i),0);
    let check = 11 - (sum % 11);
    if(check===10) check = 'X';
    if(check===11) check = 0;
    const last = s[9] === 'X' ? 'X' : parseInt(s[9],10);
    return String(check) === String(last);
  }
  return false;
}

export default { normalizeIsbn, formatIsbn, isValidIsbn };
