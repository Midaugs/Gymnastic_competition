import { api, API_BASE, clearToken } from "./api.js";

document.getElementById("logout")?.addEventListener("click", () => {
  clearToken(); location.href = "login.html";
});

const groupSelect = document.getElementById("group-select");
const createBtn = document.getElementById("create-competition");
const resultsSection = document.getElementById("results-section");
const resultsForm = document.getElementById("results-form");
const submitBtn = document.getElementById("submit-results");
const pdfLink = document.getElementById("pdf-link");

let sPart, sT, sA; // will be set by ensureStatsDom()

function ensureStatsDom() {
  let container = document.getElementById("stats");
  if (!container) {
    container = document.createElement("div");
    container.id = "stats";
    container.className = "stats";
    container.innerHTML = `
      <h3>Group Totals / Averages (participants only)</h3>
      <div class="stats-grid">
        <div></div><div>C1</div><div>C2</div><div>C3</div><div>C4</div><div>C5</div>
        <div>Participants</div><div id="s-part">0</div><div></div><div></div><div></div><div></div>
        <div>Total</div><div id="s-t1">0</div><div id="s-t2">0</div><div id="s-t3">0</div><div id="s-t4">0</div><div id="s-t5">0</div>
        <div>Average</div><div id="s-a1">0</div><div id="s-a2">0</div><div id="s-a3">0</div><div id="s-a4">0</div><div id="s-a5">0</div>
      </div>`;
    // insert before the Save button so it appears above it
    resultsSection.insertBefore(container, submitBtn);
  }
  sPart = document.getElementById("s-part");
  sT = [null,
    document.getElementById("s-t1"),
    document.getElementById("s-t2"),
    document.getElementById("s-t3"),
    document.getElementById("s-t4"),
    document.getElementById("s-t5"),
  ];
  sA = [null,
    document.getElementById("s-a1"),
    document.getElementById("s-a2"),
    document.getElementById("s-a3"),
    document.getElementById("s-a4"),
    document.getElementById("s-a5"),
  ];
}

async function init() {
  const groups = await api("/groups/");
  groupSelect.innerHTML = `<option value="" disabled selected>Select group</option>`;
  groups.forEach(g => {
    const opt = document.createElement("option");
    opt.value = g.id;
    opt.textContent = g.name;
    groupSelect.appendChild(opt);
  });
}
init().catch(e => alert("Failed to load groups: " + e.message));

let currentCompetitionId = null;
let currentChildren = [];

createBtn.addEventListener("click", async () => {
  try {
    const group_id = Number(groupSelect.value);
    const date = document.getElementById("comp-date").value;
    if (!group_id || !date) return alert("Select group and date.");

    const comp = await api("/competitions/", { method: "POST", body: { group_id, date }});
    currentCompetitionId = comp.id;

    // show section first, then ensure stats exists
    resultsSection.hidden = false;
    ensureStatsDom();

    currentChildren = await api(`/groups/${group_id}/children/`);
    renderResultsForm(currentChildren);
    pdfLink.href = `${API_BASE}/competitions/${currentCompetitionId}/pdf/`;
  } catch (e) {
    console.error(e);
    alert("Could not create competition or load children: " + e.message);
  }
});

function makeNumberInput(cls, id) {
  const input = document.createElement("input");
  input.type = "number"; input.min = "0"; input.max = "10"; input.value = "0";
  input.className = cls; input.dataset.id = id;
  input.addEventListener("input", recalcAll);
  return input;
}
function makeCheckInput(id) {
  const input = document.createElement("input");
  input.type = "checkbox"; input.checked = true;
  input.className = "part"; input.dataset.id = id;
  input.addEventListener("change", recalcAll);
  return input;
}

function renderResultsForm(children) {
  resultsForm.innerHTML = "";
  children.forEach(ch => {
    const row = document.createElement("div");
    row.className = "row"; row.dataset.childId = ch.id;

    const name = document.createElement("span");
    name.textContent = `${ch.surname} ${ch.name} (${ch.birthday})`;

    const partWrap = document.createElement("label");
    partWrap.append("Participated "); partWrap.appendChild(makeCheckInput(ch.id));

    const c1 = makeNumberInput("c1", ch.id);
    const c2 = makeNumberInput("c2", ch.id);
    const c3 = makeNumberInput("c3", ch.id);
    const c4 = makeNumberInput("c4", ch.id);
    const c5 = makeNumberInput("c5", ch.id);

    const sumEl = document.createElement("span"); sumEl.className = "sum"; sumEl.textContent = "0";
    const avgEl = document.createElement("span"); avgEl.className = "avg"; avgEl.textContent = "0";

    row.append(name, partWrap, c1, c2, c3, c4, c5, sumEl, avgEl);
    resultsForm.appendChild(row);
  });
  recalcAll(); // initial calc
}

function recalcAll() {
  // if stats weren’t created (old HTML), make them now
  if (!sPart) ensureStatsDom();

  const rows = [...resultsForm.querySelectorAll(".row")];
  let participants = 0;
  const totals = [0,0,0,0,0];

  rows.forEach(r => {
    const part = r.querySelector(".part").checked;
    const v = i => {
      const el = r.querySelector(`.c${i}`);
      const n = Number(el.value || 0);
      const clamped = Math.max(0, Math.min(10, n));
      if (n !== clamped) el.value = String(clamped);
      return clamped;
    };
    const vals = [1,2,3,4,5].map(v);
    const sum = vals.reduce((a,b) => a+b, 0);
    const avg = (sum / 5).toFixed(1);
    r.querySelector(".sum").textContent = String(sum);
    r.querySelector(".avg").textContent = avg;

    if (part) {
      participants += 1;
      for (let i=0;i<5;i++) totals[i] += vals[i];
    }
  });

  // Guard in case stats are still missing
  if (!sPart) return;

  sPart.textContent = String(participants);
  for (let i=1;i<=5;i++) {
    if (sT[i]) sT[i].textContent = String(totals[i-1]);
    if (sA[i]) sA[i].textContent = participants ? (totals[i-1] / participants).toFixed(2) : "0";
  }
}

submitBtn.addEventListener("click", async () => {
  if (!currentCompetitionId) return alert("Create a competition first.");
  const rows = [...resultsForm.querySelectorAll(".row")];
  const payload = rows.map(r => {
    const id = Number(r.dataset.childId);
    const part = r.querySelector(".part").checked;
    const get = i => Number(r.querySelector(`.c${i}`).value || 0);
    return {
      child_id: id,
      participated: part,
      criteria1: get(1),
      criteria2: get(2),
      criteria3: get(3),
      criteria4: get(4),
      criteria5: get(5),
    };
  });
  try {
    await api(`/competitions/${currentCompetitionId}/results/`, { method: "POST", body: payload });
    alert("Results saved!");
  } catch (e) {
    alert("Failed: " + e.message);
  }
});
