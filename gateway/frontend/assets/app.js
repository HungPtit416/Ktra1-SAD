const UI = (() => {
  const state = {
    customerTokenKey: 'gw_customer_token',
    staffTokenKey: 'gw_staff_token',
    customerPageSize: 8,
  };

  const $ = (id) => document.getElementById(id);

  const ensureToastRoot = () => {
    let root = document.getElementById('toast-root');
    if (!root) {
      root = document.createElement('div');
      root.id = 'toast-root';
      root.className = 'toast-root';
      document.body.appendChild(root);
    }
    return root;
  };

  const showToast = (message, type = 'info') => {
    const root = ensureToastRoot();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    root.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('leaving');
      setTimeout(() => toast.remove(), 220);
    }, 2600);
  };

  const summarizeResponse = (payload) => {
    if (!payload) return 'Done.';
    if (payload.error) return String(payload.error);

    const status = payload.status;
    const data = payload.data;

    if (typeof status === 'number' && status >= 200 && status < 300) {
      if (data && typeof data === 'object') {
        if (data.detail) return String(data.detail);
        if (data.access) return 'Login successful.';
        if (data.id) return `Operation successful (ID: ${data.id}).`;
      }
      return 'Operation successful.';
    }

    if (data && typeof data === 'object') {
      if (data.detail) return `Error: ${data.detail}`;
      if (Array.isArray(data.non_field_errors) && data.non_field_errors.length) {
        return `Error: ${data.non_field_errors[0]}`;
      }
      const firstKey = Object.keys(data)[0];
      if (firstKey) {
        const val = data[firstKey];
        if (Array.isArray(val) && val.length) return `Error: ${firstKey} - ${val[0]}`;
        return `Error: ${firstKey}`;
      }
    }

    if (typeof status === 'number') return `Request failed (${status}).`;
    return 'Updated.';
  };

  const readJson = async (response) => {
    const text = await response.text();
    try { return text ? JSON.parse(text) : {}; } catch { return { raw: text }; }
  };

  const output = (id, data) => {
    const el = $(id);
    if (el) {
      const msg = summarizeResponse(data);
      el.textContent = msg;
      el.classList.add('show');
      setTimeout(() => el.classList.remove('show'), 5000);
      return;
    }
    const status = data?.status;
    const type = typeof status === 'number' ? (status >= 200 && status < 300 ? 'success' : 'error') : (data?.error ? 'error' : 'info');
    showToast(summarizeResponse(data), type);
  };

  const headersWithToken = (key, json = false) => {
    const token = localStorage.getItem(key);
    const headers = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    if (json) headers['Content-Type'] = 'application/json';
    return headers;
  };

  const getProductImage = (type, id, name = '') => {
    // Return empty string to show CSS placeholder background
    return '';
  };

  const capitalizeType = (type) => {
    if (!type) return 'Product';
    return type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
  };

  const customizeProductNames = (products) => {
    const laptopNames = {
      1: "MacBook Pro 16\"",
      2: "Dell XPS 13",
      3: "ThinkPad X1 Carbon",
      4: "ASUS ROG Gaming Laptop",
      5: "HP Pavilion 15",
      6: "Lenovo IdeaPad 5"
    };
    
    const mobileNames = {
      1: "iPhone 15 Pro",
      2: "Samsung Galaxy S24",
      3: "Google Pixel 8",
      4: "OnePlus 12",
      5: "Xiaomi 14 Ultra",
      6: "Nothing Phone 2"
    };

    return products.map(p => {
      if (p.product_type === 'laptops' && laptopNames[p.id]) {
        p.name = laptopNames[p.id];
      } else if (p.product_type === 'mobiles' && mobileNames[p.id]) {
        p.name = mobileNames[p.id];
      }
      return p;
    });
  };

  const formatPrice = (value) => {
    const n = Number(value || 0);
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'VND' }).format(n);
  };

  const parsePathDetail = () => {
    const parts = window.location.pathname.split('/').filter(Boolean);
    const idx = parts.indexOf('products');
    if (idx >= 0 && parts.length >= idx + 3) {
      return { type: parts[idx + 1], id: Number(parts[idx + 2]) };
    }
    return null;
  };

  const fetchCatalog = async (query = '') => {
    const url = `/customer/api/products/search/?q=${encodeURIComponent(query)}`;
    const res = await fetch(url, { headers: headersWithToken(state.customerTokenKey) });
    const data = await readJson(res);
    if (!res.ok) throw new Error(`Catalog load failed: ${res.status}`);
    return data.products || [];
  };

  const renderCustomerTokenPill = (id) => {
    const el = $(id);
    if (!el) return;
    const on = !!localStorage.getItem(state.customerTokenKey);
    el.classList.toggle('on', on);
    el.textContent = on ? 'Logged in' : 'Not logged in';
    
    // Show/hide logout button
    const logoutBtn = $('customer-logout-btn');
    if (logoutBtn) {
      logoutBtn.style.display = on ? 'inline-flex' : 'none';
      if (on) {
        logoutBtn.onclick = () => {
          localStorage.removeItem(state.customerTokenKey);
          showToast('Logged out successfully.', 'success');
          setTimeout(() => window.location.href = '/customer-ui/login/', 500);
        };
      }
    }
  };

  const renderStaffTokenPill = (id) => {
    const el = $(id);
    if (!el) return;
    const on = !!localStorage.getItem(state.staffTokenKey);
    el.classList.toggle('on', on);
    el.textContent = on ? 'Logged in' : 'Not logged in';
    
    // Show/hide logout button
    const logoutBtn = $('staff-logout-btn');
    if (logoutBtn) {
      logoutBtn.style.display = on ? 'inline-flex' : 'none';
      if (on) {
        logoutBtn.onclick = () => {
          localStorage.removeItem(state.staffTokenKey);
          showToast('Logged out successfully.', 'success');
          setTimeout(() => window.location.href = '/staff-ui/login/', 500);
        };
      }
    }
  };

  const mountCustomerHome = async () => {
    const grid = $('customer-grid');
    if (!grid) return;

    const query = new URLSearchParams(window.location.search).get('q') || '';
    const viewFilter = new URLSearchParams(window.location.search).get('view') || '';
    const pageParam = Number(new URLSearchParams(window.location.search).get('page') || '1');
    const page = Number.isNaN(pageParam) || pageParam < 1 ? 1 : pageParam;
    const searchInput = $('customer-search-input');
    if (searchInput) searchInput.value = query;

    try {
      let products = await fetchCatalog(query);
      products = customizeProductNames(products);
      
      // Filter by product type if view parameter is provided
      if (viewFilter) {
        products = products.filter(p => p.product_type === viewFilter);
      }
      
      const totalPages = Math.max(1, Math.ceil(products.length / state.customerPageSize));
      const current = Math.min(page, totalPages);
      const start = (current - 1) * state.customerPageSize;
      const items = products.slice(start, start + state.customerPageSize);

      grid.innerHTML = items.map((p) => `
        <article class="card product">
          <img src="${getProductImage(p.product_type, p.id, p.name)}" alt="${p.name}" />
          <div class="product-body">
            <span class="badge">${capitalizeType(p.product_type)}</span>
            <h3>${p.name}</h3>
            <p class="price">${formatPrice(p.price)}</p>
            <a class="btn primary" href="/customer-ui/products/${p.product_type}/${p.id}/">View Details</a>
          </div>
        </article>
      `).join('') || '<p>No products available.</p>';

      const pager = $('customer-pager');
      if (pager) {
        const pageParams = `q=${encodeURIComponent(query)}${viewFilter ? `&view=${viewFilter}` : ''}`;
        const prev = current > 1 ? `<a class="btn ghost" href="?${pageParams}&page=${current - 1}">Previous</a>` : '';
        const next = current < totalPages ? `<a class="btn ghost" href="?${pageParams}&page=${current + 1}">Next</a>` : '';
        pager.innerHTML = `${prev}<span>Page ${current} / ${totalPages}</span>${next}`;
      }
    } catch (err) {
      grid.innerHTML = '<p>Failed to load products. If the API requires authentication, please log in first.</p>';
    }

    renderCustomerTokenPill('customer-token-pill');
  };

  const bindCustomerAuth = () => {
    const loginForm = $('customer-login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = $('customer-login-email').value;
        const password = $('customer-login-password').value;
        
        try {
          showToast('Logging in...', 'info');
          const res = await fetch('/customer/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
          });
          const data = await readJson(res);
          console.log('Login response:', { status: res.status, data });
          
          if (res.ok && (data.access || data.token)) {
            const token = data.access || data.token;
            localStorage.setItem(state.customerTokenKey, token);
            console.log('Token saved, redirecting...');
            showToast('Login successful!', 'success');
            setTimeout(() => {
              window.location.href = '/customer-ui/';
            }, 600);
            return;
          } else if (res.ok) {
            console.error('Response OK but no token found:', data);
            output('customer-login-output', { error: 'Login succeeded but token not found. Please try again.' });
          } else {
            const errorMsg = data.detail || data.non_field_errors?.[0] || 'Invalid credentials';
            console.error('Login failed:', errorMsg);
            output('customer-login-output', { error: errorMsg });
          }
        } catch (error) {
          console.error('Login error:', error);
          output('customer-login-output', { error: 'Network error: ' + error.message });
        }
        renderCustomerTokenPill('customer-token-pill');
      });
    }

    const registerForm = $('customer-register-form');
    if (registerForm) {
      registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = $('customer-register-name').value;
        const email = $('customer-register-email').value;
        const password = $('customer-register-password').value;
        const confirm = $('customer-register-confirm').value;
        if (password !== confirm) {
          output('customer-register-output', { error: 'Password and confirm password do not match.' });
          return;
        }
        const res = await fetch('/customer/api/auth/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password }),
        });
        output('customer-register-output', { status: res.status, data: await readJson(res) });
      });
    }


  };

  const mountCustomerDetail = async () => {
    const holder = $('customer-detail-holder');
    if (!holder) return;
    const detail = parsePathDetail();
    if (!detail) {
      holder.innerHTML = '<p>Invalid product path.</p>';
      return;
    }

    try {
      const endpoint = detail.type === 'laptop' ? `/laptops/${detail.id}/` : `/mobiles/${detail.id}/`;
      const res = await fetch(endpoint);
      const data = await readJson(res);
      if (!res.ok) {
        holder.innerHTML = '<p>Failed to load product information.</p>';
        output('customer-detail-output', { status: res.status, data });
        return;
      }

      // Customize product name for detail view
      const productType = detail.type === 'laptop' ? 'laptops' : 'mobiles';
      const productToCustomize = [{ ...data, product_type: productType, id: detail.id }];
      const customized = customizeProductNames(productToCustomize)[0];
      data.name = customized.name;

      holder.innerHTML = `
        <article class="detail-shell">
          <section class="card panel detail-media-card">
            <img class="detail-image" src="${getProductImage(detail.type, detail.id, data.name)}" alt="${data.name}" />
          </section>
          <section class="card panel detail-info-card">
            <div class="row one">
              <span class="badge">${capitalizeType(detail.type)}</span>
            </div>
            <h1>${data.name}</h1>
            <p class="price detail-price">${formatPrice(data.price)}</p>
            <div class="detail-meta">
              <p><strong>Brand:</strong> ${data.brand}</p>
              <p><strong>Specifications:</strong> ${data.specs}</p>
              <p><strong>Stock:</strong> ${data.stock}</p>
            </div>

            <section class="purchase-box">
              <h3>Quick Purchase</h3>
              <p id="detail-cart-hint" class="muted-text">Loading cart...</p>
              <div class="row">
                <select id="detail-cart-select"></select>
              <input id="detail-qty" type="number" min="1" value="1" placeholder="Quantity" />
            </div>
            <div class="actions">
              <button class="btn ghost" id="detail-create-cart-btn" type="button">Create New Cart</button>
              <button class="btn primary" id="detail-add-btn" type="button">Add to Cart</button>
              </div>
            </section>
          </section>
        </article>
      `;

      const addBtn = $('detail-add-btn');
      const createBtn = $('detail-create-cart-btn');
      const cartSelect = $('detail-cart-select');
      const hint = $('detail-cart-hint');

      const setAuthRequired = () => {
        hint.textContent = 'You must log in to add products to cart.';
        cartSelect.innerHTML = '<option value="">Not logged in</option>';
        addBtn.disabled = true;
        createBtn.disabled = true;
      };

      const getHasToken = () => !!localStorage.getItem(state.customerTokenKey);

      const loadCarts = async () => {
        const hasToken = getHasToken();
        if (!hasToken) {
          setAuthRequired();
          return;
        }

        const cartsRes = await fetch('/customer/api/carts/', {
          headers: headersWithToken(state.customerTokenKey),
        });
        const carts = await readJson(cartsRes);

        if (!cartsRes.ok) {
          hint.textContent = 'Failed to load cart list. Try logging in again.';
          addBtn.disabled = true;
          createBtn.disabled = false;
          return;
        }

        const list = Array.isArray(carts) ? carts : [];
        if (!list.length) {
          hint.textContent = 'You don\'t have a cart yet. Click "Create New Cart" to start.';
          cartSelect.innerHTML = '<option value="">No cart</option>';
          addBtn.disabled = true;
          createBtn.disabled = false;
          return;
        }

        cartSelect.innerHTML = list
          .map((c) => `<option value="${c.id}">Cart #${c.id} (${(c.items || []).length} items)</option>`)
          .join('');
        hint.textContent = 'Select a cart and quantity, then add to cart.';
        addBtn.disabled = false;
        createBtn.disabled = false;
      };

      createBtn.addEventListener('click', async () => {
        if (!getHasToken()) {
          showToast('Please log in before creating a cart.', 'error');
          return;
        }
        const resCreate = await fetch('/customer/api/carts/', {
          method: 'POST',
          headers: headersWithToken(state.customerTokenKey, true),
          body: '{}',
        });
        output('customer-detail-output', { status: resCreate.status, data: await readJson(resCreate) });
        await loadCarts();
      });

      addBtn.addEventListener('click', async () => {
        const cart = Number(cartSelect.value);
        const quantity = Number($('detail-qty').value || 1);
        if (!cart) {
          showToast('Please select a valid cart.', 'error');
          return;
        }
        if (!quantity || quantity < 1) {
          showToast('Quantity must be greater than or equal to 1.', 'error');
          return;
        }

        const addRes = await fetch('/customer/api/cart-items/', {
          method: 'POST',
          headers: headersWithToken(state.customerTokenKey, true),
          body: JSON.stringify({
            cart,
            product_type: detail.type,
            product_id: detail.id,
            quantity,
          }),
        });
        const addData = await readJson(addRes);

        const duplicateMsg = JSON.stringify(addData || {}).toLowerCase();
        if (
          addRes.status === 400
          && duplicateMsg.includes('unique set')
        ) {
          const itemsRes = await fetch('/customer/api/cart-items/', {
            headers: headersWithToken(state.customerTokenKey),
          });
          const items = await readJson(itemsRes);
          const existing = (Array.isArray(items) ? items : []).find(
            (it) => Number(it.cart) === cart && it.product_type === detail.type && Number(it.product_id) === detail.id,
          );

          if (existing) {
            const patchRes = await fetch(`/customer/api/cart-items/${existing.id}/`, {
              method: 'PATCH',
              headers: headersWithToken(state.customerTokenKey, true),
              body: JSON.stringify({ quantity: Number(existing.quantity || 0) + quantity }),
            });
            output('customer-detail-output', { status: patchRes.status, data: await readJson(patchRes) });
            return;
          }
        }

        output('customer-detail-output', { status: addRes.status, data: addData });
      });

      await loadCarts();
    } catch (err) {
      holder.innerHTML = '<p>An error occurred while loading the product details. Please try again.</p>';
      showToast('Failed to load product details.', 'error');
    }

    renderCustomerTokenPill('customer-token-pill');
  };

  const mountCustomerCart = () => {
    const cartContainer = $('customer-cart-table');
    if (!cartContainer) return;

    const buildProductMap = async () => {
      let products = await fetchCatalog('');
      products = customizeProductNames(products);
      const m = {};
      products.forEach((p) => {
        m[`${p.product_type}:${p.id}`] = {
          name: p.name,
          price: Number(p.price || 0),
          product_type: p.product_type,
        };
      });
      return m;
    };

    const loadCart = async () => {
      const [cartsRes, itemsRes, productMap] = await Promise.all([
        fetch('/customer/api/carts/', { headers: headersWithToken(state.customerTokenKey) }),
        fetch('/customer/api/cart-items/', { headers: headersWithToken(state.customerTokenKey) }),
        buildProductMap().catch(() => ({})),
      ]);

      const items = await readJson(itemsRes);
      const list = Array.isArray(items) ? items : [];
      
      if (!list.length) {
        cartContainer.innerHTML = `
          <div class="cart-empty">
            <p>Your cart is empty</p>
            <a class="btn primary" href="/customer-ui/">Continue Shopping</a>
          </div>
        `;
        const totalEl = $('customer-cart-total');
        if (totalEl) totalEl.textContent = 'Total: 0 VND';
        return;
      }

      let subtotal = 0;
      const cartItems = list.map((it) => {
        const product = productMap[`${it.product_type}:${it.product_id}`] || {};
        const price = product.price || 0;
        const itemSubtotal = price * Number(it.quantity || 0);
        subtotal += itemSubtotal;

        return `
            <div class="cart-item-row">
            <div class="cart-item-image">
              <img src="${getProductImage(it.product_type, it.product_id, product.name)}" alt="${product.name || 'Product'}" />
            </div>
            <div class="cart-item-info">
              <h3>${product.name || 'Unknown Product'}</h3>
              <p class="cart-item-type">${capitalizeType(it.product_type)}</p>
              <p class="cart-item-price">${formatPrice(price)}</p>
            </div>
            <div class="cart-item-qty-control">
              <button class="qty-btn minus" data-item-id="${it.id}" type="button">−</button>
              <input type="number" class="qty-input" data-item-id="${it.id}" value="${it.quantity}" min="1" readonly />
              <button class="qty-btn plus" data-item-id="${it.id}" type="button">+</button>
            </div>
            <div class="cart-item-subtotal">
              ${formatPrice(itemSubtotal)}
            </div>
            <button class="cart-item-remove" data-item-id="${it.id}" type="button" title="Remove from cart">✕</button>
          </div>
        `;
      }).join('');

      cartContainer.innerHTML = `
        <div class="cart-items-list">
          ${cartItems}
        </div>
        <div class="cart-summary">
          <div class="summary-row">
            <span>Subtotal:</span>
            <span class="amount">${formatPrice(subtotal)}</span>
          </div>
          <div class="summary-row">
            <span>Shipping:</span>
            <span class="amount">Free</span>
          </div>
          <div class="summary-row total">
            <span>Total:</span>
            <span class="amount">${formatPrice(subtotal)}</span>
          </div>
          <div class="checkout-actions">
            <a class="btn ghost" href="/customer-ui/">Continue Shopping</a>
            <button class="btn primary" id="checkout-btn" type="button">Checkout</button>
          </div>
        </div>
      `;

      const totalEl = $('customer-cart-total');
      if (totalEl) totalEl.textContent = `Total: ${formatPrice(subtotal)}`;

      // Bind quantity controls
      document.querySelectorAll('.qty-btn').forEach((btn) => {
        btn.addEventListener('click', async (e) => {
          const itemId = Number(btn.dataset.itemId);
          const input = document.querySelector(`.qty-input[data-item-id="${itemId}"]`);
          let newQty = Number(input.value);

          if (btn.classList.contains('plus')) {
            newQty += 1;
          } else if (btn.classList.contains('minus')) {
            newQty = Math.max(1, newQty - 1);
          }

          const patchRes = await fetch(`/customer/api/cart-items/${itemId}/`, {
            method: 'PATCH',
            headers: headersWithToken(state.customerTokenKey, true),
            body: JSON.stringify({ quantity: newQty }),
          });

          if (patchRes.ok) {
            await loadCart();
          } else {
            showToast('Failed to update quantity.', 'error');
          }
        });
      });

      // Bind remove buttons
      document.querySelectorAll('.cart-item-remove').forEach((btn) => {
        btn.addEventListener('click', async (e) => {
          const itemId = Number(btn.dataset.itemId);
          const deleteRes = await fetch(`/customer/api/cart-items/${itemId}/`, {
            method: 'DELETE',
            headers: headersWithToken(state.customerTokenKey),
          });

          if (deleteRes.ok) {
            showToast('Item removed from cart successfully.', 'success');
            await loadCart();
          } else {
            showToast('Failed to remove product.', 'error');
          }
        });
      });

      // Bind checkout button
      const checkoutBtn = $('checkout-btn');
      if (checkoutBtn) {
        checkoutBtn.addEventListener('click', () => {
          showToast('Checkout feature is under development...', 'info');
        });
      }

      if (!cartsRes.ok || !itemsRes.ok) {
        output('customer-cart-output', { status: 500, data: { detail: 'Failed to load cart data.' } });
      }
    };

    $('customer-create-cart-btn')?.addEventListener('click', async () => {
      const res = await fetch('/customer/api/carts/', {
        method: 'POST',
        headers: headersWithToken(state.customerTokenKey, true),
        body: '{}',
      });
      if (res.ok) {
        showToast('New cart created successfully.', 'success');
        await loadCart();
      } else {
        showToast('Failed to create cart.', 'error');
      }
    });

    $('customer-refresh-cart-btn')?.addEventListener('click', loadCart);

    renderCustomerTokenPill('customer-token-pill');
    loadCart();
  };

  const bindStaffAuth = () => {
    const form = $('staff-login-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = $('staff-login-email').value;
        const password = $('staff-login-password').value;
        
        try {
          showToast('Logging in...', 'info');
          const res = await fetch('/staff/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
          });
          const data = await readJson(res);
          console.log('Staff login response:', { status: res.status, data });
          
          if (res.ok && (data.access || data.token)) {
            const token = data.access || data.token;
            localStorage.setItem(state.staffTokenKey, token);
            console.log('Staff token saved, redirecting...');
            showToast('Login successful!', 'success');
            setTimeout(() => {
              window.location.href = '/staff-ui/';
            }, 600);
            return;
          } else if (res.ok) {
            console.error('Response OK but no token found:', data);
            output('staff-login-output', { error: 'Login succeeded but token not found. Please try again.' });
          } else {
            const errorMsg = data.detail || data.non_field_errors?.[0] || 'Invalid credentials';
            console.error('Staff login failed:', errorMsg);
            output('staff-login-output', { error: errorMsg });
          }
        } catch (error) {
          console.error('Staff login error:', error);
          output('staff-login-output', { error: 'Network error: ' + error.message });
        }
        renderStaffTokenPill('staff-token-pill');
      });
    }

  };

  const mountStaffDashboard = () => {
    const tbody = $('staff-products-tbody');
    if (!tbody) return;

    const params = new URLSearchParams(window.location.search);
    const type = params.get('type') || 'laptop';

    const highlightMenu = () => {
      document.querySelectorAll('[data-staff-menu]').forEach((el) => {
        if (el.getAttribute('data-staff-menu') === type) el.classList.add('on'); else el.classList.remove('on');
      });
    };

    const loadProducts = async () => {
      const res = await fetch('/staff/api/products/', { headers: headersWithToken(state.staffTokenKey) });
      const data = await readJson(res);
      const list = (data.products || []).filter((p) => p.product_type === type);
      tbody.innerHTML = list.length ? list.map((p) => `
        <tr>
          <td>${p.name}</td>
          <td>${formatPrice(p.price)}</td>
          <td>${p.brand}</td>
          <td>${p.stock}</td>
          <td><a href="/staff-ui/products/form/?type=${p.product_type}&id=${p.id}">Edit</a></td>
        </tr>
      `).join('') : '<tr><td colspan="5">No data available.</td></tr>';
      if (!res.ok) {
        output('staff-dashboard-output', { status: res.status, data });
      }
    };

    $('staff-reload-btn')?.addEventListener('click', loadProducts);

    renderStaffTokenPill('staff-token-pill');
    highlightMenu();
    loadProducts();
  };

  const mountStaffForm = () => {
    if (!$('staff-form')) return;

    const params = new URLSearchParams(window.location.search);
    const typeParam = params.get('type');
    const idParam = params.get('id');
    if (typeParam) $('staff-product-type').value = typeParam;
    if (idParam) $('staff-product-id').value = idParam;

    const payload = (includeType) => {
      const body = {
        name: $('staff-name').value,
        price: $('staff-price').value,
        brand: $('staff-brand').value,
        specs: $('staff-specs').value,
        stock: $('staff-stock').value,
      };
      if (includeType) body.product_type = $('staff-product-type').value;
      return body;
    };

    $('staff-add-btn')?.addEventListener('click', async () => {
      const res = await fetch('/staff/api/products/', {
        method: 'POST',
        headers: headersWithToken(state.staffTokenKey, true),
        body: JSON.stringify(payload(true)),
      });
      output('staff-form-output', { status: res.status, data: await readJson(res) });
    });

    $('staff-edit-btn')?.addEventListener('click', async () => {
      const id = $('staff-product-id').value;
      const type = $('staff-product-type').value;
      const res = await fetch(`/staff/api/products/${type}/${id}/`, {
        method: 'PUT',
        headers: headersWithToken(state.staffTokenKey, true),
        body: JSON.stringify(payload(false)),
      });
      output('staff-form-output', { status: res.status, data: await readJson(res) });
    });

    $('staff-delete-btn')?.addEventListener('click', async () => {
      const id = $('staff-product-id').value;
      const type = $('staff-product-type').value;
      const res = await fetch(`/staff/api/products/${type}/${id}/`, {
        method: 'DELETE',
        headers: headersWithToken(state.staffTokenKey),
      });
      output('staff-form-output', { status: res.status, data: await readJson(res) });
    });

    renderStaffTokenPill('staff-token-pill');
  };

  return {
    mountCustomerHome,
    bindCustomerAuth,
    mountCustomerDetail,
    mountCustomerCart,
    bindStaffAuth,
    mountStaffDashboard,
    mountStaffForm,
    renderCustomerTokenPill,
    renderStaffTokenPill,
  };
})();
