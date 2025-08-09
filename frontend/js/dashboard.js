import { api, clearToken } from "./api.js";

const logoutBtn = document.getElementById("logout");
logoutBtn?.addEventListener("click", () => { clearToken(); location.href = "login.html"; });

const groupsList = document.getElementById("groups");
const groupForm = document.getElementById("group-form");
const childrenSection = document.getElementById("children-section");
const groupTitle = document.getElementById("group-title");
const childForm = document.getElementById("child-form");
const childrenList = document.getElementById("children");

async function loadGroups() {
  const groups = await api("/groups/");
  groupsList.innerHTML = "";
  groups.forEach(g => {
    const li = document.createElement("li");
    li.innerHTML = `
      <strong>${g.name}</strong>
      <button data-id="${g.id}" class="view">View</button>
      <button data-id="${g.id}" class="del">Delete</button>`;
    groupsList.appendChild(li);
  });
}

groupsList?.addEventListener("click", async (e) => {
  const t = e.target;
  if (t.matches(".view")) {
    const id = t.getAttribute("data-id");
    await showChildren(id);
  }
  if (t.matches(".del")) {
    const id = t.getAttribute("data-id");
    if (confirm("Delete group?")) {
      await api(`/groups/${id}`, { method: "DELETE" });
      childrenSection.hidden = true;
      await loadGroups();
    }
  }
});

groupForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = groupForm.name.value.trim();
  if (!name) return;
  await api("/groups/", { method: "POST", body: { name } });
  groupForm.reset();
  await loadGroups();
});

async function showChildren(groupId) {
  const groups = await api("/groups/");
  const g = groups.find(x => String(x.id) === String(groupId));
  groupTitle.textContent = g ? g.name : "";
  childrenSection.hidden = false;
  childrenList.innerHTML = "";
  const kids = await api(`/groups/${groupId}/children/`);
  kids.forEach(c => {
    const li = document.createElement("li");
    li.textContent = `${c.surname} ${c.name} — ${c.birthday}`;
    childrenList.appendChild(li);
  });
  childForm.onsubmit = async (e) => {
    e.preventDefault();
    const payload = {
      name: childForm.name.value,
      surname: childForm.surname.value,
      birthday: childForm.birthday.value
    };
    await api(`/groups/${groupId}/children/`, { method: "POST", body: payload });
    childForm.reset();
    await showChildren(groupId);
  };
}

loadGroups().catch(err => alert(err.message));
