const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const path = require('path');
const multer = require('multer');
const bcrypt = require('bcryptjs');
const Database = require('better-sqlite3');

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize SQLite database
const db = new Database('./database/local_database.db');

// Create tables
db.exec(`
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        vk_user_id INTEGER,
        flag TEXT DEFAULT 'main',
        orders INTEGER DEFAULT 0,
        message_id INTEGER DEFAULT -1,
        mailling INTEGER DEFAULT 1,
        balance FLOAT DEFAULT 0,
        role TEXT DEFAULT 'user',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS staff (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        staff_group TEXT,
        staff_date TEXT,
        balance FLOAT DEFAULT 0,
        raything FLOAT DEFAULT 5,
        reproofs INTEGER DEFAULT 0,
        orders_all INTEGER DEFAULT 0,
        orders_did INTEGER DEFAULT 0,
        orders_no_does INTEGER DEFAULT 0,
        dialog_all INTEGER DEFAULT 0,
        dialog_did INTEGER DEFAULT 0,
        dialog_no_does INTEGER DEFAULT 0,
        can_work_designer INTEGER DEFAULT 0,
        can_work_manager INTEGER DEFAULT 0,
        blokopad_id INTEGER
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS staff_perms (
        user_id INTEGER,
        perms TEXT
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT,
        about TEXT,
        price INTEGER,
        carousel_photo TEXT,
        attachment TEXT,
        link TEXT,
        priority INTEGER,
        alias TEXT
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service TEXT,
        status TEXT DEFAULT 'Просматривается',
        number INTEGER,
        data TEXT,
        designer_id INTEGER,
        manager_id INTEGER,
        chat_id INTEGER,
        attachment TEXT,
        have_manager INTEGER DEFAULT 0,
        it_skin INTEGER DEFAULT 0,
        arms TEXT,
        attachment_no_key TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS promocodes (
        promocode TEXT PRIMARY KEY,
        sale FLOAT,
        used_count INTEGER DEFAULT 0
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS used_promocode (
        user_id INTEGER,
        promocode TEXT
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS pay_list (
        user_id INTEGER,
        money FLOAT,
        id_form TEXT,
        designer INTEGER,
        service TEXT,
        bet FLOAT
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS design_settings (
        on_free_avatar INTEGER DEFAULT 0,
        reviews INTEGER DEFAULT 0
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS help_messages (
        user_id INTEGER,
        message_id INTEGER
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS order_messages (
        user_id INTEGER,
        message_id INTEGER
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS dialogs_count (
        manager INTEGER DEFAULT 0,
        designer INTEGER DEFAULT 0
    )
`);

db.exec(`
    CREATE TABLE IF NOT EXISTS admin_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE,
        user_id INTEGER,
        expires_at TEXT
    )
`);

// Insert default settings if not exists
const settingsCount = db.prepare('SELECT COUNT(*) as count FROM design_settings').get();
if (settingsCount.count === 0) {
    db.exec(`INSERT INTO design_settings (on_free_avatar, reviews) VALUES (0, 0)`);
}

// Insert default admin if not exists
const adminCount = db.prepare('SELECT COUNT(*) as count FROM users WHERE role = ?').get('admin');
if (adminCount.count === 0) {
    const hashedPassword = bcrypt.hashSync('admin123', 10);
    db.prepare('INSERT INTO users (username, password, role, vk_user_id) VALUES (?, ?, ?, ?)').run('admin', hashedPassword, 'admin', 501285409);
}

// Insert default staff admin
const staffAdmin = db.prepare('SELECT COUNT(*) as count FROM staff WHERE user_id = ?').get(501285409);
if (staffAdmin.count === 0) {
    db.prepare('INSERT INTO staff (user_id, name, staff_group, staff_date, balance, raything, can_work_designer, can_work_manager) VALUES (?, ?, ?, ?, ?, ?, ?, ?)').run(
        501285409, 'Илья', 'admin', new Date().toISOString(), 1000000, 5, 1, 1
    );
    db.prepare('INSERT INTO staff_perms (user_id, perms) VALUES (?, ?)').run(501285409, '*');
}

// Middleware
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// File upload configuration
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + '-' + file.originalname);
    }
});
const upload = multer({ storage });

// Ensure uploads directory exists
const fs = require('fs');
if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
}

// Session middleware
app.use(session({
    secret: 'your-secret-key-change-in-production',
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false, maxAge: 24 * 60 * 60 * 1000 }
}));

// Auth middleware
const requireAuth = (req, res, next) => {
    if (req.session.userId) {
        next();
    } else {
        res.redirect('/login');
    }
};

const requireAdmin = (req, res, next) => {
    if (req.session.userId) {
        const user = db.prepare('SELECT role FROM users WHERE user_id = ?').get(req.session.userId);
        if (user && user.role === 'admin') {
            next();
        } else {
            res.redirect('/dashboard');
        }
    } else {
        res.redirect('/login');
    }
};

// Routes

// Home
app.get('/', (req, res) => {
    if (req.session.userId) {
        res.redirect('/dashboard');
    } else {
        res.redirect('/login');
    }
});

// Registration
app.get('/register', (req, res) => {
    res.render('register', { error: null });
});

app.post('/register', async (req, res) => {
    const { username, password, confirmPassword } = req.body;
    
    if (!username || !password) {
        return res.render('register', { error: 'Все поля обязательны' });
    }
    
    if (password !== confirmPassword) {
        return res.render('register', { error: 'Пароли не совпадают' });
    }
    
    try {
        const existingUser = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
        if (existingUser) {
            return res.render('register', { error: 'Пользователь уже существует' });
        }
        
        const hashedPassword = await bcrypt.hash(password, 10);
        db.prepare('INSERT INTO users (username, password) VALUES (?, ?)').run(username, hashedPassword);
        
        res.redirect('/login');
    } catch (error) {
        console.error('Registration error:', error);
        res.render('register', { error: 'Ошибка регистрации' });
    }
});

// Login
app.get('/login', (req, res) => {
    res.render('login', { error: null });
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    
    try {
        const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);
        
        if (!user) {
            return res.render('login', { error: 'Пользователь не найден' });
        }
        
        const validPassword = await bcrypt.compare(password, user.password);
        
        if (!validPassword) {
            return res.render('login', { error: 'Неверный пароль' });
        }
        
        req.session.userId = user.user_id;
        req.session.username = user.username;
        req.session.role = user.role;
        
        res.redirect('/dashboard');
    } catch (error) {
        console.error('Login error:', error);
        res.render('login', { error: 'Ошибка входа' });
    }
});

// Logout
app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/login');
});

// Dashboard
app.get('/dashboard', requireAuth, (req, res) => {
    const user = db.prepare('SELECT * FROM users WHERE user_id = ?').get(req.session.userId);
    const orders = db.prepare('SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC').all(req.session.userId);
    
    res.render('dashboard', { 
        user, 
        orders,
        username: req.session.username 
    });
});

// Services
app.get('/services', requireAuth, (req, res) => {
    const services = db.prepare('SELECT * FROM services ORDER BY priority').all();
    res.render('services', { services, username: req.session.username });
});

// Create Order
app.get('/order/new', requireAuth, (req, res) => {
    const services = db.prepare('SELECT * FROM services ORDER BY priority').all();
    const settings = db.prepare('SELECT * FROM design_settings').get();
    res.render('order_new', { services, settings, username: req.session.username });
});

app.post('/order/create', requireAuth, upload.array('attachments'), (req, res) => {
    const { service, description, arms } = req.body;
    const attachments = req.files ? req.files.map(f => f.path).join(',') : '';
    
    const order = db.prepare('SELECT * FROM services WHERE service = ?').get(service);
    let itSkin = 0;
    
    if (service.toLowerCase().includes('скин')) {
        itSkin = 1;
    } else if (service.toLowerCase().includes('оформление профиля')) {
        itSkin = 2;
    }
    
    const result = db.prepare(`
        INSERT INTO orders (user_id, service, status, data, attachment, it_skin, arms, number) 
        VALUES (?, ?, 'Просматривается', ?, ?, ?, ?, (SELECT COALESCE(MAX(number), 0) + 1 FROM orders))
    `).run(req.session.userId, service, description, attachments, itSkin, arms || '');
    
    db.prepare('UPDATE users SET orders = orders + 1 WHERE user_id = ?').run(req.session.userId);
    
    res.redirect('/dashboard?order_created=' + result.lastInsertRowid);
});

// View Order
app.get('/order/:id', requireAuth, (req, res) => {
    const order = db.prepare('SELECT * FROM orders WHERE id = ? AND user_id = ?').get(req.params.id, req.session.userId);
    if (!order) {
        return res.redirect('/dashboard');
    }
    res.render('order_view', { order, username: req.session.username });
});

// Help
app.get('/help', requireAuth, (req, res) => {
    res.render('help', { username: req.session.username });
});

app.post('/help/send', requireAuth, (req, res) => {
    const { message } = req.body;
    db.prepare('INSERT INTO help_messages (user_id, message_id) VALUES (?, ?)').run(req.session.userId, Date.now());
    res.redirect('/help?sent=1');
});

// Admin Panel
app.get('/admin', requireAdmin, (req, res) => {
    const stats = {
        users: db.prepare('SELECT COUNT(*) as count FROM users').get().count,
        orders: db.prepare('SELECT COUNT(*) as count FROM orders').get().count,
        pendingOrders: db.prepare("SELECT COUNT(*) as count FROM orders WHERE status = 'Просматривается'").get().count,
        staff: db.prepare('SELECT COUNT(*) as count FROM staff').get().count
    };
    
    const recentOrders = db.prepare('SELECT * FROM orders ORDER BY created_at DESC LIMIT 10').all();
    const users = db.prepare('SELECT user_id, username, role, created_at FROM users ORDER BY created_at DESC').all();
    
    res.render('admin/index', { stats, recentOrders, users, username: req.session.username });
});

// Admin - Orders Management
app.get('/admin/orders', requireAdmin, (req, res) => {
    const filter = req.query.filter || 'all';
    let query;
    
    switch(filter) {
        case 'pending':
            query = "SELECT * FROM orders WHERE status = 'Просматривается' ORDER BY created_at DESC";
            break;
        case 'in_progress':
            query = "SELECT * FROM orders WHERE status = 'Выполняется' ORDER BY created_at DESC";
            break;
        case 'completed':
            query = "SELECT * FROM orders WHERE status = 'Выполнен' ORDER BY created_at DESC";
            break;
        default:
            query = 'SELECT * FROM orders ORDER BY created_at DESC';
    }
    
    const orders = db.prepare(query).all();
    res.render('admin/orders', { orders, filter, username: req.session.username });
});

// Admin - Update Order Status
app.post('/admin/order/:id/status', requireAdmin, (req, res) => {
    const { status, designer_id, manager_id } = req.body;
    db.prepare('UPDATE orders SET status = ?, designer_id = ?, manager_id = ? WHERE id = ?').run(
        status, designer_id || null, manager_id || null, req.params.id
    );
    res.redirect('/admin/orders');
});

// Admin - Users Management
app.get('/admin/users', requireAdmin, (req, res) => {
    const users = db.prepare('SELECT * FROM users ORDER BY created_at DESC').all();
    res.render('admin/users', { users, username: req.session.username });
});

// Admin - Staff Management
app.get('/admin/staff', requireAdmin, (req, res) => {
    const staff = db.prepare('SELECT s.*, p.perms FROM staff s LEFT JOIN staff_perms p ON s.user_id = p.user_id').all();
    res.render('admin/staff', { staff, username: req.session.username });
});

app.post('/admin/staff/add', requireAdmin, (req, res) => {
    const { user_id, name, staff_group, perms } = req.body;
    
    db.prepare(`
        INSERT OR REPLACE INTO staff (user_id, name, staff_group, staff_date, can_work_designer, can_work_manager) 
        VALUES (?, ?, ?, ?, 1, 1)
    `).run(user_id, name, staff_group, new Date().toISOString());
    
    if (perms) {
        db.prepare('INSERT OR REPLACE INTO staff_perms (user_id, perms) VALUES (?, ?)').run(user_id, perms);
    }
    
    res.redirect('/admin/staff');
});

// Admin - Services Management
app.get('/admin/services', requireAdmin, (req, res) => {
    const services = db.prepare('SELECT * FROM services ORDER BY priority').all();
    res.render('admin/services', { services, username: req.session.username });
});

app.post('/admin/service/add', requireAdmin, (req, res) => {
    const { service, about, price, link, priority, alias } = req.body;
    db.prepare(`
        INSERT INTO services (service, about, price, link, priority, alias) 
        VALUES (?, ?, ?, ?, ?, ?)
    `).run(service, about, price || 0, link || '', priority || 0, alias || '');
    res.redirect('/admin/services');
});

app.post('/admin/service/:id/delete', requireAdmin, (req, res) => {
    db.prepare('DELETE FROM services WHERE id = ?').run(req.params.id);
    res.redirect('/admin/services');
});

// Admin - Settings
app.get('/admin/settings', requireAdmin, (req, res) => {
    const settings = db.prepare('SELECT * FROM design_settings').get();
    res.render('admin/settings', { settings, username: req.session.username });
});

app.post('/admin/settings', requireAdmin, (req, res) => {
    const { on_free_avatar, reviews } = req.body;
    db.prepare('UPDATE design_settings SET on_free_avatar = ?, reviews = ?').run(
        on_free_avatar ? 1 : 0, reviews ? 1 : 0
    );
    res.redirect('/admin/settings');
});

// Admin - Promocodes
app.get('/admin/promocodes', requireAdmin, (req, res) => {
    const promocodes = db.prepare('SELECT * FROM promocodes').all();
    res.render('admin/promocodes', { promocodes, username: req.session.username });
});

app.post('/admin/promocode/add', requireAdmin, (req, res) => {
    const { promocode, sale } = req.body;
    db.prepare('INSERT OR REPLACE INTO promocodes (promocode, sale) VALUES (?, ?)').run(promocode, sale);
    res.redirect('/admin/promocodes');
});

// Profile
app.get('/profile', requireAuth, (req, res) => {
    const user = db.prepare('SELECT * FROM users WHERE user_id = ?').get(req.session.userId);
    const staff = db.prepare('SELECT * FROM staff WHERE user_id = ?').get(req.session.userId);
    res.render('profile', { user, staff, username: req.session.username });
});

// API for VK Bot integration (optional)
app.post('/api/vk/webhook', (req, res) => {
    // VK Bot webhook endpoint - can be implemented to sync with website
    res.json({ ok: true });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Admin panel: http://localhost:${PORT}/admin`);
    console.log(`Default admin credentials: admin / admin123`);
});
