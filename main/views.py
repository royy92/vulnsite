from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import BlogPost, User
import sqlite3, os
from django.conf import settings
from django.db import connection

# Create your views here.
def home(request):
    return render(request, "index.html")


def _session_uid(request):
    # لو مافي uid بالسيشن (أول دخول)، بنعطي 1 بشكل افتراضي
    return request.session.get('uid', 1)



# 1️⃣  SQL Injection
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # ضعف مقصود: استعلام مدموج قابل للحقن
        sql = f"SELECT id, username FROM main_user WHERE username='{username}' AND password='{password}'"
        with connection.cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()

        if row:
            request.session['uid'] = row[0]            # Django سيحفظ الـ session بدون تعارض أقفال
            return redirect(f"/dashboard/?id={row[0]}")  # 👈 IDOR مقصود
        return HttpResponse("Invalid credentials")
    return render(request, "login.html")


def dashboard(request):
    user_id = request.GET.get("id", "1")   # 👈 ضعف IDOR
    sql = f"SELECT id, username, password FROM main_user WHERE id={user_id}"  # 👈 حتى قابلة للحقن
    with connection.cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
    return render(request, "dashboard.html", {"row": row, "raw_id": user_id})

    uid = request.GET.get("id") or _session_uid(request)  # 👈 لا نعرضه للمستخدم
    with connection.cursor() as cur:
        cur.execute(f"SELECT id, username FROM main_user WHERE id={uid}")  # ضعيف لو لعبت بـ id
        row = cur.fetchone()
    ctx = {"uid": uid, "username": row[1] if row else "user"}
    return render(request, "dashboard.html", ctx)



def profile_api(request):
    uid = request.GET.get("id") or _session_uid(request)
    with connection.cursor() as cur:
        cur.execute(f"SELECT id, username, password FROM main_user WHERE id={uid}")  # 👈 IDOR + SQL concat
        row = cur.fetchone()
    if not row:
        return JsonResponse({"error": "not found"}, status=404)
    return JsonResponse({"id": row[0], "username": row[1], "password": row[2]})



# 2️⃣  Stored XSS
def blog(request):
    error = None
    if request.method == "POST":
        title = (request.POST.get("title") or "").strip()
        content = (request.POST.get("content") or "").strip()

        if title and content:
            p = BlogPost.objects.create(title=title, content=content, author="Guest")
            # Immediately after publishing, we will direct you to the details page (if there is a script, it will work there)
            return redirect('post_detail', pk=p.id)

    posts = BlogPost.objects.all().order_by("-id")
    return render(request, "blog.html", {"posts": posts, "error": error})



def post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, "post_detail.html", {"post": post})



# 3️⃣  File Upload
def upload(request):
    if request.method == "POST":
        f = request.FILES['file']
        os.makedirs(os.path.join(settings.BASE_DIR, "uploads"), exist_ok=True)
        with open(os.path.join(settings.BASE_DIR, "uploads", f.name), "wb+") as dest:
            for chunk in f.chunks():
                dest.write(chunk)
        return HttpResponse("File uploaded!")
    return render(request, "upload.html")

UPLOAD_DIR = os.path.join(settings.BASE_DIR, "uploads")

def files_index(request):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    items = sorted(os.listdir(UPLOAD_DIR))
    html = "<h2>Uploads Index (Public)</h2><ul>"
    for name in items:
        html += f'<li><a href="/files/{name}">{name}</a></li>'
    html += "</ul>"
    return HttpResponse(html)



# robots.txt (leak sensetive data)
def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /uploads/\n"
        "Disallow: /backup/db.sqlite3\n"
    )
    return HttpResponse(content, content_type="text/plain")
