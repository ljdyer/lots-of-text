import pickle
import os
from os.path import join
import jiwer
from collections import Counter
from memo.memo import memo
from math import prod as product


TEXT_FILE_PATH = 'text_files'
PICKLE_PATH = 'nb.pickle'

class NB_Splitter():

    def __init__(self):
        self.word_freqs = Counter()
        print('Initialized')

    def train(self, files):
        # Get word frequencies
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                words = f.read().split()
                self.word_freqs.update(words)
        # Get total number of tokens
        self.N = sum(freq for freq in self.word_freqs.values())
        print(self.N)
        # Define probability distribution
        self.Pdist = {word: freq / self.N for word, freq in self.word_freqs.items()}
        # Pickle trained model
        with open(PICKLE_PATH, 'wb') as f:
            pickle.dump(self, f)

    @memo
    def segment(self, text):
        if not text:
            return []
        candidates = ([first] + self.segment(rem) for first, rem in self.splits(text))
        return max(candidates, key=self.Pwords)

    @staticmethod
    def splits(text, L=20):
        return [(text[:i+1], text[i+1:]) for i in range(min(len(text), L))]

    def Pwords(self, words):
        """Get NB probability of a sequence of words"""
        return product(self.Pw(w) for w in words)

    def Pw(self, word):
        if word in self.Pdist:
            return self.Pdist[word]
        else:
            return 10./(self.N * 10 ** len(word))


def split_every_five_chars(remaining, words_so_far=None):

    if not words_so_far:
        words_so_far = []
    if len(remaining) > 4:
        words_so_far.append(remaining[:5])
        remaining = remaining[5:]
        return split_every_five_chars(remaining, words_so_far)
    else:
        if remaining:
            words_so_far.append(remaining)
        return ' '.join(words_so_far)


if __name__ == "__main__":

    files = [join(TEXT_FILE_PATH, file_name)
             for file_name in os.listdir(TEXT_FILE_PATH)
             if file_name.endswith('.txt')]
    nb_splitter = NB_Splitter()
    print(nb_splitter.word_freqs)
    nb_splitter.train(files)
    print(nb_splitter.word_freqs.most_common(10))

    # with open(PICKLE_PATH, 'rb') as f:
    #     hmm = pickle.load(f)

    raw_text = """Saida Aden Said: I still have this horrific image in my mind. I could see people falling down, gunshots. I was so terrified. Really, I was crying a lot. Someone who knew my father and my mom grabbed my hand, and he said, "Let's go! Let's go! Let's go!" And I was like, "Where's my mom? My mom? My mom?"Noria Dambrine Dusabireme: During nights we would hear shots, we would hear guns. Elections were supposed to happen. We had young people going in the street, they were having strikes. And most of the young people died.SAS: We boarded a vehicle. It was overloaded. People were running for their lives. That is how I fled from Somalia. My mom missed me. Nobody told her where I went.NDD: The fact that we did not go to school, we couldn't go to the market, we were just stuck home made me realize that if I got an option to go for something better, I could just go for it and have a better future.(Music)Ignazio Matteini: Globally, displaced people in the world have been increasing. Now there are almost 60 million people displaced in the world. And unfortunately, it doesn't stop.Chrystina Russell: I think the humanitarian community is starting to realize from research and reality that we're talking about a much more permanent problem.Baylie Damtie Yeshita: These students, they need a tertiary education, a degree that they can use. If the students are living now in Rwanda, if they get relocated, still they can continue their study. Still, their degree is useful, wherever they are.CR: Our audacious project was to really test Southern New Hampshire University's Global Education Movement's ability to scale, to bring bachelor's degrees and pathways to employment to refugees and those who would otherwise not have access to higher education.SAS: It was almost impossible, as a refugee person, to further my education and to make my career. My name is Saida Aden Said, and I am from Somalia. I was nine years old when I came to Kakuma, and I started going to school at 17. Now I am doing my bachelor degree with SNHU.NDD: My name is Noria Dambrine Dusabireme. I'm doing my bachelor of arts in communications with a concentration in business.CR: We are serving students across five different countries: Lebanon, Kenya, Malawi, Rwanda and South Africa. Really proud to have 800 AA grads to over 400 bachelor's graduates and nearly 1,000 students enrolled right now.So, the magic of this is that we're addressing refugee lives as they exist. There are no classes. There are no lectures. There are no due dates. There are no final exams. This degree is competency-based and not time-bound. You choose when you start your project. You choose how you're going to approach it.NDD: When you open the platform, that's where you can see the goals. Under each goal, we can find projects. When you open a project, you get the competencies that you have to master, directions and overview of the project.CR: The secret sauce of SNHU is combining that competency-based online learning with the in-person learning that we do with partners to provide all the wraparound supports. That includes academic coaching. It means psychosocial support, medical support, and it's also that back-end employment support that's really resulting in the 95 percent graduation, the 88 percent employment.NDD: I'm a social media management intern. It's related to the communications degree I'm doing. I've learned so many things out of the project and in the real world.CR: The structured internship is really an opportunity for students to practice their skills, for us to create connections between that internship and a later job opportunity.(Music)This is a model that really stops putting time and university policies and procedures at the center and instead puts the student at the center.IM: The SNHU model is a big way to shake the tree. Huge. It's a huge shake to the traditional way of having tertiary education here.BDY: It can transform the lives of students from these vulnerable and refugee communities.NDD: If I get the degree, I can just come back and work everywhere that I want. I can go for a masters confidently in English, which is something that I would not have dreamt of before. And I have the confidence and the skills required to actually go out and just tackle the workplace without having to fear that I can't make it.SAS: I always wanted to work with the community. I want to establish a nonprofit. We advocate for women's education. I want to be someone who is, like, an ambassador and encourage them to learn and tell them it is never too late. It's a dream."""
    raw_text = raw_text[:100]
    original_text = ''.join([c.lower() for c in raw_text if c.isalpha() 
                             or c == ' '])
    print(original_text)
    
    text = ''.join([c.lower() for c in original_text if c.isalpha()])
    print(text)

    hypothesis_dumb = split_every_five_chars(text)
    print(hypothesis_dumb)
    hypothesis_nb = ' '.join(nb_splitter.segment(text))
    print(hypothesis_nb)

    print(jiwer.cer(original_text, text))
    print(jiwer.cer(original_text, hypothesis_dumb))
    print(jiwer.cer(original_text, hypothesis_nb))
