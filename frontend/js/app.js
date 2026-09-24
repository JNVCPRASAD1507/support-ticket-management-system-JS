
/**
 * Main dashboard application (vanilla JS SPA)
 */

if (!requireAuth()) {
  /* redirected */
}

const user = getCurrentUser();
document.getElementById("user-name").textContent = user?.name || "User";
document.getElementById("user-role").textContent = user?.role || "";

if (isAdmin()) {
  document.getElementById("nav-users").classList.remove("hidden");
}

document.getElementById("logout-btn").addEventListener("click", logout);

// Navigation
const content = document.getElementById("content");
const pageTitle = document.getElementById("page-title");
const topbarActions = document.getElementById("topbar-actions");

document.querySelectorAll(".sidebar-nav a").forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    document.querySelectorAll(".sidebar-nav a").forEach((a) => a.classList.remove("active"));
    link.classList.add("active");
    const view = link.dataset.view;
    navigate(view);
  });
});

function navigate(view) {
  topbarActions.innerHTML = "";
  switch (view) {
    case "tickets":
      pageTitle.textContent = "Tickets";
      loadTickets();
      break;
    case "create":
      pageTitle.textContent = "Create Ticket";
      showCreateTicket();
      break;
    case "categories":
      pageTitle.textContent = "Categories";
      loadCategories();
      break;
    case "users":
      pageTitle.textContent = "Users";
      loadUsers();
      break;
    case "notifications":
      pageTitle.textContent = "Notifications";
      loadNotifications();
      break;
    default:
      loadTickets();
  }
}

// ========== Tickets ==========
let ticketPage = 1;
let ticketFilters = { search: "", status: "", priority: "", category_id: "" };

async function loadTickets() {
  content.innerHTML = `<div class="loading">Loading tickets…</div>`;
  try {
    const params = new URLSearchParams({
      page: ticketPage,
      page_size: 15,
    });
    if (ticketFilters.search) params.set("search", ticketFilters.search);
    if (ticketFilters.status) params.set("status_filter", ticketFilters.status);
    if (ticketFilters.priority) params.set("priority", ticketFilters.priority);
    if (ticketFilters.category_id) params.set("category_id", ticketFilters.category_id);

    const data = await api.get(`/tickets?${params}`);
    const categories = await api.get("/categories?active_only=true").catch(() => []);

    const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));

    content.innerHTML = `
      <div class="stats-grid">
        <div class="stat-card"><div class="label">Total Tickets</div><div class="value">${data.total}</div></div>
        <div class="stat-card"><div class="label">Page</div><div class="value">${data.page} / ${totalPages}</div></div>
      </div>
      <div class="card">
        <div class="filters">
          <input type="text" id="filter-search" placeholder="Search…" value="${escapeHtml(ticketFilters.search)}" />
          <select id="filter-status">
            <option value="">All statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
          <select id="filter-priority">
            <option value="">All priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
          <select id="filter-category">
            <option value="">All categories</option>
            ${(categories || []).map((c) => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join("")}
          </select>
          <button class="btn btn-primary btn-sm" id="btn-apply-filters">Apply</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Title</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              ${
                data.items.length === 0
                  ? `<tr><td colspan="6" class="empty-state">No tickets found</td></tr>`
                  : data.items
                      .map(
                        (t) => `
                <tr>
                  <td>${escapeHtml(t.ticket_number || t.id)}</td>
                  <td>${escapeHtml(t.title)}</td>
                  <td><span class="badge badge-${t.status}">${t.status}</span></td>
                  <td><span class="badge badge-${t.priority}">${t.priority}</span></td>
                  <td>${formatDate(t.created_at)}</td>
                  <td><button class="btn btn-secondary btn-sm" data-ticket-id="${t.id}">View</button></td>
                </tr>`
                      )
                      .join("")
              }
            </tbody>
          </table>
        </div>
        <div class="pagination">
          <button class="btn btn-secondary btn-sm" id="prev-page" ${ticketPage <= 1 ? "disabled" : ""}>← Prev</button>
          <span>Page ${ticketPage} of ${totalPages}</span>
          <button class="btn btn-secondary btn-sm" id="next-page" ${ticketPage >= totalPages ? "disabled" : ""}>Next →</button>
        </div>
      </div>
    `;

    // Restore filter values
    document.getElementById("filter-status").value = ticketFilters.status;
    document.getElementById("filter-priority").value = ticketFilters.priority;
    document.getElementById("filter-category").value = ticketFilters.category_id;

    document.getElementById("btn-apply-filters").addEventListener("click", () => {
      ticketFilters.search = document.getElementById("filter-search").value.trim();
      ticketFilters.status = document.getElementById("filter-status").value;
      ticketFilters.priority = document.getElementById("filter-priority").value;
      ticketFilters.category_id = document.getElementById("filter-category").value;
      ticketPage = 1;
      loadTickets();
    });

    document.getElementById("prev-page")?.addEventListener("click", () => {
      if (ticketPage > 1) {
        ticketPage--;
        loadTickets();
      }
    });
    document.getElementById("next-page")?.addEventListener("click", () => {
      if (ticketPage < totalPages) {
        ticketPage++;
        loadTickets();
      }
    });

    content.querySelectorAll("[data-ticket-id]").forEach((btn) => {
      btn.addEventListener("click", () => openTicketDetail(btn.dataset.ticketId));
    });
  } catch (err) {
    content.innerHTML = `<div class="alert alert-error">${escapeHtml(err.message)}</div>`;
  }
}

async function openTicketDetail(ticketId) {
  content.innerHTML = `<div class="loading">Loading ticket…</div>`;
  try {
    const [ticket, comments, attachments, categories, agents] = await Promise.all([
      api.get(`/tickets/${ticketId}`),
      api.get(`/comments/tickets/${ticketId}`).catch(() => []),
      api.get(`/attachments/tickets/${ticketId}`).catch(() => []),
      api.get("/categories?active_only=true").catch(() => []),
      isAdmin() ? api.get("/users?page=1&page_size=100").catch(() => ({ items: [] })) : Promise.resolve({ items: [] }),
    ]);

    content.innerHTML = `
      <div class="card">
        <div class="card-header">
          <h3>${escapeHtml(ticket.ticket_number)} — ${escapeHtml(ticket.title)}</h3>
          <button class="btn btn-secondary btn-sm" id="back-to-list">← Back</button>
        </div>
        <div class="detail-grid">
          <div class="detail-item"><label>Status</label><div class="val"><span class="badge badge-${ticket.status}">${ticket.status}</span></div></div>
          <div class="detail-item"><label>Priority</label><div class="val"><span class="badge badge-${ticket.priority}">${ticket.priority}</span></div></div>
          <div class="detail-item"><label>Category ID</label><div class="val">${ticket.category_id}</div></div>
          <div class="detail-item"><label>Assigned To</label><div class="val">${ticket.assigned_to_id ?? "—"}</div></div>
          <div class="detail-item"><label>SLA Due</label><div class="val">${ticket.sla_due_at ? formatDate(ticket.sla_due_at) : "—"}</div></div>
          <div class="detail-item"><label>Created</label><div class="val">${formatDate(ticket.created_at)}</div></div>
        </div>
        <div class="form-group">
          <label>Description</label>
          <p style="white-space:pre-wrap">${escapeHtml(ticket.description)}</p>
        </div>

        <div style="display:flex;flex-wrap:wrap;gap:0.75rem;margin:1.25rem 0;">
          <select id="new-status" style="padding:0.45rem 0.7rem;background:var(--bg);border:1px solid var(--border);border-radius:8px;color:var(--text)">
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
          <button class="btn btn-primary btn-sm" id="btn-change-status">Update Status</button>
          ${
            isAdmin()
              ? `
            <select id="assign-user" style="padding:0.45rem 0.7rem;background:var(--bg);border:1px solid var(--border);border-radius:8px;color:var(--text)">
              <option value="">Unassign</option>
              ${(agents.items || [])
                .filter((u) => u.role === "agent" || u.role === "admin")
                .map((u) => `<option value="${u.id}" ${ticket.assigned_to_id == u.id ? "selected" : ""}>${escapeHtml(u.name)}</option>`)
                .join("")}
            </select>
            <button class="btn btn-secondary btn-sm" id="btn-assign">Assign</button>
            <button class="btn btn-danger btn-sm" id="btn-delete-ticket">Delete</button>
          `
              : ""
          }
        </div>
      </div>

      <div class="card">
        <h3 style="margin-bottom:0.75rem">Comments</h3>
        <div class="comments-list" id="comments-list">
          ${(comments || []).length === 0
            ? `<p class="empty-state">No comments yet</p>`
            : (comments || [])
                .map(
                  (c) => `
            <div class="comment">
              <div class="comment-meta">User #${c.user_id || c.created_by_id || "?"} · ${formatDate(c.created_at)}</div>
              <div>${escapeHtml(c.content || c.body || "")}</div>
            </div>`
                )
                .join("")}
        </div>
        <div class="form-group" style="margin-top:1rem">
          <textarea id="comment-text" placeholder="Write a comment…"></textarea>
        </div>
        <button class="btn btn-primary btn-sm" id="btn-add-comment">Add Comment</button>
      </div>

      <div class="card">
        <h3 style="margin-bottom:0.75rem">Attachments</h3>
        <ul id="attachments-list" style="list-style:none;margin-bottom:1rem">
          ${(attachments || []).length === 0
            ? `<li class="empty-state">No attachments</li>`
            : (attachments || [])
                .map(
                  (a) => `
            <li style="padding:0.4rem 0;border-bottom:1px solid var(--border)">
              ${escapeHtml(a.filename || a.file_name || "file")} 
              <button class="btn btn-danger btn-sm" data-del-att="${a.id}" style="margin-left:0.5rem">Delete</button>
            </li>`
                )
                .join("")}
        </ul>
        <input type="file" id="file-input" />
        <button class="btn btn-secondary btn-sm" id="btn-upload" style="margin-top:0.5rem">Upload</button>
      </div>
    `;

    document.getElementById("new-status").value = ticket.status;
    document.getElementById("back-to-list").addEventListener("click", () => navigate("tickets"));

    document.getElementById("btn-change-status").addEventListener("click", async () => {
      try {
        await api.patch(`/tickets/${ticketId}/status`, {
          status: document.getElementById("new-status").value,
        });
        openTicketDetail(ticketId);
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("btn-add-comment").addEventListener("click", async () => {
      const text = document.getElementById("comment-text").value.trim();
      if (!text) return;
      try {
        await api.post(`/comments/tickets/${ticketId}`, { content: text });
        openTicketDetail(ticketId);
      } catch (err) {
        try {
          await api.post(`/comments/tickets/${ticketId}`, { body: text });
          openTicketDetail(ticketId);
        } catch (err2) {
          alert(err2.message || err.message);
        }
      }
    });

    document.getElementById("btn-upload").addEventListener("click", async () => {
      const fileInput = document.getElementById("file-input");
      if (!fileInput.files.length) return alert("Select a file first");
      const fd = new FormData();
      fd.append("file", fileInput.files[0]);
      try {
        await api.upload(`/attachments/tickets/${ticketId}`, fd);
        openTicketDetail(ticketId);
      } catch (err) {
        alert(err.message);
      }
    });

    content.querySelectorAll("[data-del-att]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        if (!confirm("Delete this attachment?")) return;
        try {
          await api.delete(`/attachments/${btn.dataset.delAtt}`);
          openTicketDetail(ticketId);
        } catch (err) {
          alert(err.message);
        }
      });
    });

    if (isAdmin()) {
      document.getElementById("btn-assign")?.addEventListener("click", async () => {
        const val = document.getElementById("assign-user").value;
        try {
          await api.patch(`/tickets/${ticketId}/assign`, {
            assigned_to_id: val ? parseInt(val, 10) : null,
          });
          openTicketDetail(ticketId);
        } catch (err) {
          alert(err.message);
        }
      });
      document.getElementById("btn-delete-ticket")?.addEventListener("click", async () => {
        if (!confirm("Delete this ticket permanently?")) return;
        try {
          await api.delete(`/tickets/${ticketId}`);
          navigate("tickets");
        } catch (err) {
          alert(err.message);
        }
      });
    }
  } catch (err) {
    content.innerHTML = `<div class="alert alert-error">${escapeHtml(err.message)}</div>
      <button class="btn btn-secondary" onclick="navigate('tickets')">Back</button>`;
  }
}

// ========== Create Ticket ==========
async function showCreateTicket() {
  let categories = [];
  try {
    categories = await api.get("/categories?active_only=true");
  } catch (_) {}

  content.innerHTML = `
    <div class="card" style="max-width:560px">
      <form id="create-ticket-form">
        <div class="form-group">
          <label>Title</label>
          <input type="text" id="t-title" required minlength="3" maxlength="200" placeholder="Brief summary" />
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea id="t-desc" required minlength="5" placeholder="Describe the issue…"></textarea>
        </div>
        <div class="form-group">
          <label>Priority</label>
          <select id="t-priority">
            <option value="low">Low</option>
            <option value="medium" selected>Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        <div class="form-group">
          <label>Category</label>
          <select id="t-category" required>
            <option value="">Select category</option>
            ${(categories || []).map((c) => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join("")}
          </select>
        </div>
        <div id="create-alert" class="alert hidden"></div>
        <button type="submit" class="btn btn-primary" id="btn-create">Create Ticket</button>
      </form>
    </div>
  `;

  document.getElementById("create-ticket-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const alertEl = document.getElementById("create-alert");
    const btn = document.getElementById("btn-create");
    btn.disabled = true;
    try {
      const ticket = await api.post("/tickets", {
        title: document.getElementById("t-title").value.trim(),
        description: document.getElementById("t-desc").value.trim(),
        priority: document.getElementById("t-priority").value,
        category_id: parseInt(document.getElementById("t-category").value, 10),
      });
      alertEl.className = "alert alert-success";
      alertEl.textContent = `Ticket ${ticket.ticket_number} created!`;
      alertEl.classList.remove("hidden");
      setTimeout(() => openTicketDetail(ticket.id), 800);
    } catch (err) {
      alertEl.className = "alert alert-error";
      alertEl.textContent = err.message;
      alertEl.classList.remove("hidden");
    } finally {
      btn.disabled = false;
    }
  });
}

// ========== Categories ==========
async function loadCategories() {
  content.innerHTML = `<div class="loading">Loading…</div>`;
  try {
    const categories = await api.get("/categories");
    content.innerHTML = `
      <div class="card">
        <div class="card-header">
          <h3>All Categories</h3>
          ${isAdmin() ? `<button class="btn btn-primary btn-sm" id="btn-new-cat">+ New Category</button>` : ""}
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Name</th><th>Description</th><th>Active</th></tr></thead>
            <tbody>
              ${(categories || [])
                .map(
                  (c) => `
                <tr>
                  <td>${c.id}</td>
                  <td>${escapeHtml(c.name)}</td>
                  <td>${escapeHtml(c.description || "—")}</td>
                  <td>${c.is_active ? "✅" : "❌"}</td>
                </tr>`
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </div>
    `;

    if (isAdmin()) {
      document.getElementById("btn-new-cat")?.addEventListener("click", () => {
        const name = prompt("Category name:");
        if (!name) return;
        const description = prompt("Description (optional):") || null;
        api
          .post("/categories", { name, description })
          .then(() => loadCategories())
          .catch((err) => alert(err.message));
      });
    }
  } catch (err) {
    content.innerHTML = `<div class="alert alert-error">${escapeHtml(err.message)}</div>`;
  }
}

// ========== Users (admin) ==========
async function loadUsers() {
  if (!isAdmin()) {
    content.innerHTML = `<div class="alert alert-error">Admin only</div>`;
    return;
  }
  content.innerHTML = `<div class="loading">Loading users…</div>`;
  try {
    const data = await api.get("/users?page=1&page_size=50");
    content.innerHTML = `
      <div class="card">
        <div class="table-wrap">
          <table>
            <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Active</th></tr></thead>
            <tbody>
              ${(data.items || [])
                .map(
                  (u) => `
                <tr>
                  <td>${u.id}</td>
                  <td>${escapeHtml(u.name)}</td>
                  <td>${escapeHtml(u.email)}</td>
                  <td><span class="badge badge-open">${u.role}</span></td>
                  <td>${u.is_active ? "✅" : "❌"}</td>
                </tr>`
                )
                .join("")}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<div class="alert alert-error">${escapeHtml(err.message)}</div>`;
  }
}

// ========== Notifications ==========
async function loadNotifications() {
  content.innerHTML = `<div class="loading">Loading…</div>`;
  try {
    const list = await api.get("/notifications").catch(() => []);
    const items = Array.isArray(list) ? list : list.items || [];
    content.innerHTML = `
      <div class="card">
        ${
          items.length === 0
            ? `<p class="empty-state">No notifications</p>`
            : items
                .map(
                  (n) => `
            <div class="comment" style="opacity:${n.is_read ? 0.6 : 1}">
              <div class="comment-meta">${formatDate(n.created_at)} ${n.is_read ? "" : "· New"}</div>
              <div>${escapeHtml(n.message || n.title || JSON.stringify(n))}</div>
            </div>`
                )
                .join("")
        }
      </div>
    `;
  } catch (err) {
    content.innerHTML = `<div class="alert alert-error">${escapeHtml(err.message)}</div>`;
  }
}

// ========== Helpers ==========
function escapeHtml(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

// Expose navigate for inline handlers
window.navigate = navigate;

// Initial view
navigate("tickets");


