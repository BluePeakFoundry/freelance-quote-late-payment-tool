const money = (value) => Math.round((Number(value) + Number.EPSILON) * 100) / 100;
const eur = (value) => `${money(value).toFixed(2)} EUR`;

function numberFrom(id) {
  const value = Number(document.getElementById(id).value);
  if (!Number.isFinite(value)) throw new Error(`${id} is not numeric`);
  return value;
}

function requireRange(name, value, min, max) {
  if (value < min || value > max) throw new Error(`${name} must be between ${min} and ${max}`);
}

function calculate() {
  const client = document.getElementById('client').value.trim() || 'Client';
  const project = document.getElementById('project').value.trim() || 'Project';
  const net = money(numberFrom('net'));
  const hours = numberFrom('hours');
  const vatRate = numberFrom('vat');
  const withholdingRate = numberFrom('withholding');
  const platformFeeRate = numberFrom('platformFee');
  const bufferRate = numberFrom('buffer');
  const minHourly = numberFrom('minHourly');
  const dueDays = Math.trunc(numberFrom('dueDays'));
  const lateDays = Math.trunc(numberFrom('lateDays'));
  const lateRate = numberFrom('lateRate');

  requireRange('net fee', net, 1, 1000000);
  requireRange('hours', hours, 0.25, 10000);
  [vatRate, withholdingRate, platformFeeRate, bufferRate, lateRate].forEach((v) => requireRange('percentage', v, 0, 100));
  requireRange('due days', dueDays, 0, 365);
  requireRange('late days', lateDays, 0, 3650);

  const vat = money(net * vatRate / 100);
  const withholding = money(net * withholdingRate / 100);
  const platformFee = money(net * platformFeeRate / 100);
  const buffer = money(net * bufferRate / 100);
  const total = money(net + vat - withholding);
  const takehome = money(net - platformFee - buffer);
  const hourly = money(takehome / hours);
  const target = money(minHourly * hours);
  const gap = money(Math.max(0, target - takehome));
  const due = new Date();
  due.setDate(due.getDate() + dueDays);
  const dueIso = due.toISOString().slice(0, 10);
  const lateInterest = money(total * lateRate / 100 * lateDays / 365);

  document.getElementById('netOut').textContent = eur(net);
  document.getElementById('vatOut').textContent = eur(vat);
  document.getElementById('withholdingOut').textContent = `-${eur(withholding)}`;
  document.getElementById('totalOut').textContent = eur(total);
  document.getElementById('hourlyOut').textContent = `${hourly.toFixed(2)} EUR/h`;
  document.getElementById('marginOut').textContent = gap === 0 ? 'OK' : `Short by ${eur(gap)}`;
  document.getElementById('dueOut').textContent = dueIso;
  document.getElementById('lateOut').textContent = eur(lateInterest);

  document.getElementById('proposal').value = `Proposal for ${client}: ${project}. Net fee: ${eur(net)}. Editable VAT: ${vatRate}% (${eur(vat)}). Editable withholding: ${withholdingRate}% (${eur(withholding)}). Total due: ${eur(total)}. Estimated hours: ${hours}; effective pre-income-tax/gross-expense hourly amount: ${hourly.toFixed(2)} EUR/h.`;
  document.getElementById('reminder').value = `Friendly reminder for ${client}: the ${project} invoice is due on ${dueIso} for ${eur(total)}. If paid ${lateDays} days late at an editable annual rate of ${lateRate}%, the informational late amount would be ${eur(lateInterest)}.`;
}

function copyFrom(id) {
  const field = document.getElementById(id);
  field.select();
  field.setSelectionRange(0, field.value.length);
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(field.value).catch(() => document.execCommand('copy'));
  } else {
    document.execCommand('copy');
  }
}

document.querySelectorAll('input').forEach((input) => input.addEventListener('input', () => {
  try { calculate(); } catch (err) { console.warn(err.message); }
}));
document.getElementById('copyProposal').addEventListener('click', () => copyFrom('proposal'));
document.getElementById('copyReminder').addEventListener('click', () => copyFrom('reminder'));

calculate();
