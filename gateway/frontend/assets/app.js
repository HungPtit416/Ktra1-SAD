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
    const url = `http://localhost:8101/api/products/search/?q=${encodeURIComponent(query)}`;
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
          localStorage.removeItem('gw_customer_cart_id');
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
          const res = await fetch('http://localhost:8101/api/auth/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
          });
          const data = await readJson(res);
          console.log('Login response:', { status: res.status, data });
          
          if (res.ok && (data.access || data.token)) {
            const token = data.access || data.token;
            // Clear old cart ID when switching users
            localStorage.removeItem('gw_customer_cart_id');
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
        const res = await fetch('http://localhost:8101/api/auth/register/', {
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
      const endpoint = detail.type === 'laptop' ? `http://localhost:8100/laptops/${detail.id}/?t=${Date.now()}` : `http://localhost:8100/mobiles/${detail.id}/?t=${Date.now()}`;
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

      const hasToken = !!localStorage.getItem(state.customerTokenKey);
      const isOutOfStock = data.stock === 0;
      const stockStatus = isOutOfStock 
        ? `<p style="color: #EF4444; font-weight: 600;">❌ Hết hàng</p>`
        : `<p style="color: #10B981; font-weight: 600;">✓ Còn ${data.stock} sản phẩm</p>`;
      
      const actionSection = hasToken 
        ? `<section class="purchase-box">
             <h3>Thêm vào giỏ hàng</h3>
             <div class="row">
               ${isOutOfStock ? stockStatus : `<input id="detail-qty" type="number" min="1" max="${data.stock}" value="1" placeholder="Số lượng" />`}
             </div>
             <div class="actions">
               <button class="btn primary" id="detail-add-btn" type="button" ${isOutOfStock ? 'disabled' : ''}>
                 ${isOutOfStock ? 'Sản phẩm đã hết hàng' : 'Thêm vào giỏ hàng'}
               </button>
             </div>
           </section>`
        : `<section class="purchase-box">
             <p class="login-hint">Vui lòng <a href="/customer-ui/login/">đăng nhập</a> để mua hàng</p>
             <div class="actions">
               <a class="btn primary" href="/customer-ui/login/">Đăng nhập</a>
             </div>
           </section>`;

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
              <p><strong>Hãng sản xuất:</strong> ${data.brand}</p>
              <p><strong>Thông số:</strong> ${data.specs}</p>
              <p><strong>Số lượng có sẵn:</strong> ${stockStatus}</p>
            </div>
            ${actionSection}
          </section>
        </article>
      `;

      if (hasToken && !isOutOfStock) {
        const addBtn = $('detail-add-btn');
        // Reset button state
        addBtn.disabled = false;
        addBtn.addEventListener('click', async () => {
          const quantity = Number($('detail-qty').value || 1);
          if (!quantity || quantity < 1) {
            showToast('Vui lòng nhập số lượng hợp lệ.', 'error');
            return;
          }
          if (quantity > data.stock) {
            showToast(`Số lượng không được vượt quá ${data.stock}.`, 'error');
            return;
          }

          try {
            // Check if user is logged in first
            const token = localStorage.getItem(state.customerTokenKey);
            if (!token) {
              showToast('Vui lòng đăng nhập trước khi thêm vào giỏ hàng.', 'error');
              addBtn.disabled = false;
              // Redirect to login after delay
              setTimeout(() => window.location.href = '/customer-ui/login/', 1000);
              return;
            }

            addBtn.disabled = true;
            showToast('Đang thêm...', 'info');

            // Get or create cart
            let cartId = localStorage.getItem('gw_customer_cart_id');
            if (!cartId) {
              const createCartRes = await fetch('http://localhost:8100/cart/api/carts/', {
                method: 'POST',
                headers: headersWithToken(state.customerTokenKey, true),
                body: '{}',
              });
              if (!createCartRes.ok) {
                showToast('Lỗi khi tạo giỏ hàng.', 'error');
                addBtn.disabled = false;
                return;
              }
              const newCart = await readJson(createCartRes);
              cartId = newCart.id;
              localStorage.setItem('gw_customer_cart_id', cartId);
            }

            // Add item to cart
            const addRes = await fetch('http://localhost:8100/cart/api/cart-items/', {
              method: 'POST',
              headers: headersWithToken(state.customerTokenKey, true),
              body: JSON.stringify({
                cart: Number(cartId),
                product_type: detail.type,
                product_id: detail.id,
                quantity,
                price: data.price,
              }),
            });

            if (addRes.ok) {
              showToast('Đã thêm vào giỏ hàng!', 'success');
              setTimeout(() => {
                window.location.href = '/customer-ui/cart/';
              }, 600);
            } else {
              const err = await readJson(addRes);
              const errorMsg = err.error || err.detail || 'Không thể thêm vào giỏ hàng';
              showToast(`Lỗi: ${errorMsg}`, 'error');
              addBtn.disabled = false;
            }
          } catch (error) {
            console.error('Add to cart error:', error);
            showToast('Lỗi: ' + error.message, 'error');
            addBtn.disabled = false;
          }
        });
      }
    } catch (err) {
      holder.innerHTML = '<p>Lỗi khi tải thông tin sản phẩm. Vui lòng thử lại.</p>';
      console.error('Detail load error:', err);
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
        fetch('http://localhost:8100/cart/api/carts/', { headers: headersWithToken(state.customerTokenKey) }),
        fetch('http://localhost:8100/cart/api/cart-items/', { headers: headersWithToken(state.customerTokenKey) }),
        buildProductMap().catch(() => ({})),
      ]);

      const itemsData = await readJson(itemsRes);
      // Handle both array format and pagination format
      const list = Array.isArray(itemsData) ? itemsData : (itemsData.results || []);
      
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

          const patchRes = await fetch(`http://localhost:8100/cart/api/cart-items/${itemId}/`, {
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
          const deleteRes = await fetch(`http://localhost:8100/cart/api/cart-items/${itemId}/`, {
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
        checkoutBtn.addEventListener('click', async () => {
          if (!list.length) {
            showToast('Giỏ hàng trống, không thể thanh toán.', 'error');
            return;
          }

          try {
            checkoutBtn.disabled = true;
            showToast('Đang tạo đơn hàng...', 'info');

            // Create order from cart items
            const orderItems = list.map(item => ({
              product_type: item.product_type,
              product_id: item.product_id,
              quantity: item.quantity,
              price: productMap[`${item.product_type}:${item.product_id}`]?.price || 0,
            }));

            const createOrderRes = await fetch('http://localhost:8100/order/api/orders/', {
              method: 'POST',
              headers: headersWithToken(state.customerTokenKey, true),
              body: JSON.stringify({
                items: orderItems,
                total_amount: subtotal,
                status: 'confirmed',
              }),
            });

            if (!createOrderRes.ok) {
              const err = await readJson(createOrderRes);
              showToast(`Lỗi tạo đơn: ${err.detail || 'Lỗi không xác định'}`, 'error');
              checkoutBtn.disabled = false;
              return;
            }

            const order = await readJson(createOrderRes);
            console.log('Order created:', order);

            // Delete all cart items
            const deletePromises = list.map(item =>
              fetch(`http://localhost:8100/cart/api/cart-items/${item.id}/`, {
                method: 'DELETE',
                headers: headersWithToken(state.customerTokenKey),
              })
            );
            await Promise.all(deletePromises);

            // Clear saved cart ID
            localStorage.removeItem('gw_customer_cart_id');

            showToast('Đơn hàng đã được tạo thành công!', 'success');
            setTimeout(() => {
              window.location.href = '/customer-ui/orders/';
            }, 1000);
          } catch (error) {
            console.error('Checkout error:', error);
            showToast('Lỗi: ' + error.message, 'error');
            checkoutBtn.disabled = false;
          }
        });
      }

      if (!cartsRes.ok || !itemsRes.ok) {
        output('customer-cart-output', { status: 500, data: { detail: 'Failed to load cart data.' } });
      }
    };



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
          const res = await fetch('http://localhost:8102/api/auth/login/', {
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
      const res = await fetch('http://localhost:8102/api/products/', { headers: headersWithToken(state.staffTokenKey) });
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
      const res = await fetch('http://localhost:8102/api/products/', {
        method: 'POST',
        headers: headersWithToken(state.staffTokenKey, true),
        body: JSON.stringify(payload(true)),
      });
      output('staff-form-output', { status: res.status, data: await readJson(res) });
    });

    $('staff-edit-btn')?.addEventListener('click', async () => {
      const id = $('staff-product-id').value;
      const type = $('staff-product-type').value;
      const res = await fetch(`http://localhost:8102/api/products/${type}/${id}/`, {
        method: 'PUT',
        headers: headersWithToken(state.staffTokenKey, true),
        body: JSON.stringify(payload(false)),
      });
      output('staff-form-output', { status: res.status, data: await readJson(res) });
    });

    $('staff-delete-btn')?.addEventListener('click', async () => {
      const id = $('staff-product-id').value;
      const type = $('staff-product-type').value;
      const res = await fetch(`http://localhost:8102/api/products/${type}/${id}/`, {
        method: 'DELETE',
        headers: headersWithToken(state.staffTokenKey),
      });
      output('staff-form-output', { status: res.status, data: await readJson(res) });
    });

    renderStaffTokenPill('staff-token-pill');
  };

  const mountCustomerOrders = async () => {
    const container = $('customer-orders-container');
    if (!container) return;

    try {
      const ordersRes = await fetch('http://localhost:8100/order/api/orders/', {
        headers: headersWithToken(state.customerTokenKey),
      });

      if (!ordersRes.ok) {
        container.innerHTML = '<p>Lỗi khi tải đơn hàng.</p>';
        return;
      }

      const allOrders = await readJson(ordersRes);
      const orders = Array.isArray(allOrders) ? allOrders : (allOrders.results || []);

      if (!orders.length) {
        container.innerHTML = `
          <div class="orders-empty">
            <p>Bạn chưa có đơn hàng nào.</p>
            <a class="btn primary" href="/customer-ui/">Tiếp tục mua sắm</a>
          </div>
        `;
        return;
      }

      const ordersHtml = orders.map(order => `
        <div class="card panel order-card" style="margin-bottom: 1.5rem;">
          <div class="order-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--line); padding-bottom: 1rem;">
            <h3>Đơn hàng #${order.id}</h3>
            <span class="badge" style="background: ${order.status === 'confirmed' ? 'var(--success)' : order.status === 'delivered' ? 'var(--accent)' : 'var(--ink-light)'}; color: white;">
              ${order.status}
            </span>
          </div>
          <div class="order-info" style="margin-bottom: 1rem;">
            <p><strong>Ngày đặt:</strong> ${new Date(order.created_at).toLocaleString('vi-VN')}</p>
            <p><strong>Tổng tiền:</strong> <strong style="color: var(--accent); font-size: 1.2rem;">${formatPrice(order.total_amount)}</strong></p>
          </div>
          <div class="order-items">
            <h4 style="margin-bottom: 0.8rem;">Sản phẩm:</h4>
            ${(order.items || []).map(item => `
              <div style="display: flex; gap: 1rem; padding: 0.8rem; background: var(--bg); border-radius: var(--radius); margin-bottom: 0.5rem;">
                <div style="flex: 1;">
                  <p><strong>${capitalizeType(item.product_type)} #${item.product_id}</strong></p>
                  <p style="color: var(--ink-light); font-size: 0.9rem;">Số lượng: ${item.quantity}</p>
                </div>
                <div style="text-align: right;">
                  <p style="color: var(--accent); font-weight: 600;">${formatPrice(item.price)}</p>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `).join('');

      container.innerHTML = ordersHtml;
    } catch (error) {
      console.error('Orders load error:', error);
      container.innerHTML = '<p>Lỗi khi tải đơn hàng: ' + error.message + '</p>';
    }

    renderCustomerTokenPill('customer-token-pill');
  };

  return {
    mountCustomerHome,
    bindCustomerAuth,
    mountCustomerDetail,
    mountCustomerCart,
    mountCustomerOrders,
    bindStaffAuth,
    mountStaffDashboard,
    mountStaffForm,
    renderCustomerTokenPill,
    renderStaffTokenPill,
  };
})();

// Handle browser back/forward navigation
window.addEventListener('popstate', () => {
  location.reload();
});

