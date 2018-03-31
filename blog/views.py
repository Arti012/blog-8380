from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator
from pprint import pprint

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='cd73d756-063c-4695-a394-f39b8a7b6be6',
        password='pHsDFFjo4yff',
        version='2016-05-19 ')

    language_translator = LanguageTranslator(
        username='a012de2f-b7e7-4b17-9d19-b11f154af0f7',
        password='7KtAIOtOqQqC')

    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        posting = post.text
        toneObj = json.dumps(tone_analyzer.tone(tone_input=posting,
                                                content_type="text/plain"), indent=2)
        post.toneObj2 = json.loads(toneObj)
        post.angerScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][0]['score']
        post.disgustScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][1]['score']
        post.fearScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][2]['score']
        post.joyScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][3]['score']
        post.sadScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][4]['score']

        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='es')
        print(translation)

        translation_1 = translation['translations'][0]['translation']
        tran = translation['word_count']
        tran_2= translation['character_count']
        wc = "  Word Count:"
        cc = "  Character Count:"
        translation_new = translation_1
        translation_1 =   wc +str(tran) +" |"+ cc + str(tran_2)
        obj = json.dumps(translation_new, indent=2, ensure_ascii=False)
        obj_n = json.dumps(translation_1, indent=2, ensure_ascii=False)
        #obj = json.loads(obj)

        post.obj2 = json.loads(obj)
        post.obj3 = json.loads(obj_n)
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
