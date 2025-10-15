// ===== API helpers =====
async function apiGetProducts() {
  const res = await fetch("/api/products");
  return await res.json();
}

async function apiDeleteProduct(id) {
  await fetch(`/api/products/${id}`, { method: "DELETE" });
}

async function apiCreateProduct(payload) {
  const res = await fetch("/api/products", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Add failed: " + (err.error || res.statusText));
  }
}

async function apiUpdateProduct(id, payload) {
  const res = await fetch(`/api/products/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Update failed: " + (err.error || res.statusText));
  }
}

// ===== UI logic =====
async function loadProducts() {
  const data = await apiGetProducts();
  const list = document.getElementById("productList");
  list.innerHTML = "";

  data.forEach((p) => {
    const li = document.createElement("li");

    const span = document.createElement("span");
    const categoryName = p.category ? p.category.name : "—";
    span.innerHTML = `
    <div class="product-info">
      <div class="product-name">${p.name}</div>
      <div class="product-meta">
        <span class="product-price">$${p.price}</span>
        <span class="product-status ${p.status === "available" ? "status-ok" : "status-bad"}">${p.status}</span>
        <span class="product-category">${categoryName}</span>
      </div>
    </div>
  `;
  

    const actions = document.createElement("div");
    actions.style.display = "flex";
    actions.style.gap = "8px";

    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.classList.add("edit-btn");
    editBtn.onclick = () => switchToEdit(li, p);

    const delBtn = document.createElement("button");
    delBtn.textContent = "Delete";
    delBtn.classList.add("delete-btn");
    delBtn.onclick = async () => {
      await apiDeleteProduct(p.id);
      loadProducts();
    };

    actions.appendChild(editBtn);
    actions.appendChild(delBtn);

    const row = document.createElement("div");
    row.style.display = "flex";
    row.style.justifyContent = "space-between";
    row.style.width = "100%";
    row.appendChild(span);
    row.appendChild(actions);

    li.appendChild(row);
    list.appendChild(li);
  });
}

function switchToEdit(li, product) {
  li.innerHTML = ""; // очистили элемент

  const form = document.createElement("div");
  form.classList.add("edit-form");

  const title = document.createElement("h4");
  title.textContent = `Edit Product #${product.id}`;
  form.appendChild(title);

  // helper для строки
  function addField(labelText, defaultValue, type = "text") {
    const group = document.createElement("div");
    group.classList.add("edit-row");

    const label = document.createElement("label");
    label.textContent = labelText;
    const input = document.createElement("input");
    input.type = type;
    input.value = defaultValue;

    group.appendChild(label);
    group.appendChild(input);
    form.appendChild(group);
    return input;
  }

  const nameInput = addField("Name:", product.name);
  const priceInput = addField("Price:", product.price, "number");
  const statusInput = addField("Status:", product.status);

  const btns = document.createElement("div");
  btns.classList.add("edit-buttons");

  const saveBtn = document.createElement("button");
  saveBtn.textContent = "Save";
  saveBtn.classList.add("save-btn");
  saveBtn.onclick = async () => {
    const payload = {
      name: nameInput.value.trim(),
      price: Number(priceInput.value),
      status: statusInput.value.trim(),
    };
    await apiUpdateProduct(product.id, payload);
    loadProducts();
  };

  const cancelBtn = document.createElement("button");
  cancelBtn.textContent = "Cancel";
  cancelBtn.classList.add("cancel-btn");
  cancelBtn.onclick = () => loadProducts();

  btns.appendChild(saveBtn);
  btns.appendChild(cancelBtn);
  form.appendChild(btns);

  li.appendChild(form);
}

// ===== Load categories =====
async function loadCategories() {
  const res = await fetch("/api/categories");
  if (!res.ok) {
    alert("Failed to load categories");
    return;
  }
  const categories = await res.json();
  const select = document.getElementById("category-select");
  select.innerHTML = '<option value="">— select category —</option>';
  categories.forEach((cat) => {
    const option = document.createElement("option");
    option.value = cat.id;
    option.textContent = cat.name;
    select.appendChild(option);
  });
}

// ===== Add product =====
async function addProduct() {
  const name = document.getElementById("name").value.trim();
  const price = parseFloat(document.getElementById("price").value);
  const status = document.getElementById("status").value;
  const categoryId = document.getElementById("category-select").value;

  if (!name || !price) {
    alert("Please fill in name and price");
    return;
  }

  const payload = {
    name,
    price,
    status,
    category_id: categoryId ? parseInt(categoryId) : null,
  };

  await apiCreateProduct(payload);
  await loadProducts();

  // очистка формы
  document.getElementById("name").value = "";
  document.getElementById("price").value = "";
  document.getElementById("category-select").value = "";
}

// ===== Инициализация =====
document.addEventListener("DOMContentLoaded", async () => {
  await loadCategories();
  await loadProducts();
});
