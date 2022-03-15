import pickle
from os.path import join
import jiwer

TEXT_FILE_PATH = 'text_files'
PICKLE_PATH = 'hmm.pickle'


class HMM():

    def __init__(self):

        self.state_list = ['B', 'M', 'E', 'S']
        self.Count_dic = {}
        self.line_num = 0
        self.A_dic = {}
        self.B_dic = {}
        self.Pi_dic = {}
        for state in self.state_list:
            self.A_dic[state] = {s: 0.0 for s in self.state_list}
            self.Pi_dic[state] = 0.0
            self.B_dic[state] = {}
            self.Count_dic[state] = 0

    @staticmethod
    def make_label(text):

        out_text = []
        if len(text) == 1:
            out_text.append('S')
        else:
            out_text += ['B'] + ['M'] * (len(text) - 2) + ['E']
        return out_text

    def train(self, files):

        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                text = ''.join([c.lower() for c in f.read().strip() if c.isalpha() or c == ' '])
                if not text:
                    print("Couldn't get text from file!")
                    continue

                char_list = [c for c in text if c != ' ']
                word_list = text.split()
                state_list = []
                for w in word_list:
                    state_list.extend(self.make_label(w))
                try:
                    assert len(char_list) == len(state_list)
                except AssertionError:
                    print('Char list and state list have different lengths.')
                    continue

                for k, v in enumerate(state_list):

                    # Count_dic counts total occurences of statuses (B,M,E,S)
                    self.Count_dic[v] += 1
                    # pi_dic counts starting statuses (B,M,E,S)
                    if k == 0:
                        self.Pi_dic[v] += 1
                    else:
                        # Transition probability
                        self.A_dic[state_list[k-1]][v] += 1
                        # Word frequencies
                        self.B_dic[state_list[k]][char_list[k]] = \
                            self.B_dic[state_list[k]].get(char_list[k], 0) + 1

        self.num_files = len(files)

        # Calculate probabilities
        self.Pi_dic = {k: v * 1.0 / self.num_files
                       for k, v in self.Pi_dic.items()}
        self.A_dic = {k: {k1: v1 / self.Count_dic[k] for k1, v1 in v.items()}
                      for k, v in self.A_dic.items()}
        self.B_dic = {k: {k1: (v1 + 1) / self.Count_dic[k]
                          for k1, v1 in v.items()}
                      for k, v in self.B_dic.items()}
        with open(PICKLE_PATH, 'wb') as f:
            pickle.dump(self, f)

    def viterbi(self, text, states, start_p, trans_p, emit_p):

        V = [{}]
        path = {}
        for y in states:
            V[0][y] = start_p[y] * emit_p[y].get(text[0], 0)
            path[y] = [y]
        for t in range(1, len(text)):
            V.append({})
            newpath = {}

            never_seen = not any([text[t] in emit_p[state].keys() for state in states])

            for y in states:
                emitP = emit_p[y].get(text[t], 0) if not never_seen else 1
                (prob, state) = max(
                    [(V[t - 1][y0] * trans_p[y0].get(y, 0) *
                        emitP, y0)
                     for y0 in states if V[t - 1][y0] > 0])
                V[t][y] = prob
                newpath[y] = path[state] + [y]
            path = newpath

        if emit_p['M'].get(text[-1], 0) > emit_p['S'].get(text[-1], 0):
            (prob, state) = max([(V[len(text) - 1][y], y) for y in ('E', 'M')])
        else:
            (prob, state) = max([(V[len(text) - 1][y], y) for y in states])

        return prob, path[state]

    def cut(self, text):

        prob, pos_list = self.viterbi(text, self.state_list, self.Pi_dic, self.A_dic, self.B_dic)

        begin, next = 0, 0
        for i, char in enumerate(text):
            pos = pos_list[i]
            if pos == 'B':
                begin = i
            elif pos == 'E':
                yield text[begin: i + 1]
                next = i + 1
            elif pos == 'S':
                yield char
                next = i + 1
        if next < len(text):
            yield text[next:]


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

    # files = [join(TEXT_FILE_PATH, file_name)
    #          for file_name in os.listdir(TEXT_FILE_PATH)
    #          if file_name.endswith('.txt')]
    # hmm = HMM()
    # hmm.train(files)

    with open(PICKLE_PATH, 'rb') as f:
        hmm = pickle.load(f)

    raw_text = """Saida Aden Said: I still have this horrific image in my mind. I could see people falling down, gunshots. I was so terrified. Really, I was crying a lot. Someone who knew my father and my mom grabbed my hand, and he said, "Let's go! Let's go! Let's go!" And I was like, "Where's my mom? My mom? My mom?"Noria Dambrine Dusabireme: During nights we would hear shots, we would hear guns. Elections were supposed to happen. We had young people going in the street, they were having strikes. And most of the young people died.SAS: We boarded a vehicle. It was overloaded. People were running for their lives. That is how I fled from Somalia. My mom missed me. Nobody told her where I went.NDD: The fact that we did not go to school, we couldn't go to the market, we were just stuck home made me realize that if I got an option to go for something better, I could just go for it and have a better future.(Music)Ignazio Matteini: Globally, displaced people in the world have been increasing. Now there are almost 60 million people displaced in the world. And unfortunately, it doesn't stop.Chrystina Russell: I think the humanitarian community is starting to realize from research and reality that we're talking about a much more permanent problem.Baylie Damtie Yeshita: These students, they need a tertiary education, a degree that they can use. If the students are living now in Rwanda, if they get relocated, still they can continue their study. Still, their degree is useful, wherever they are.CR: Our audacious project was to really test Southern New Hampshire University's Global Education Movement's ability to scale, to bring bachelor's degrees and pathways to employment to refugees and those who would otherwise not have access to higher education.SAS: It was almost impossible, as a refugee person, to further my education and to make my career. My name is Saida Aden Said, and I am from Somalia. I was nine years old when I came to Kakuma, and I started going to school at 17. Now I am doing my bachelor degree with SNHU.NDD: My name is Noria Dambrine Dusabireme. I'm doing my bachelor of arts in communications with a concentration in business.CR: We are serving students across five different countries: Lebanon, Kenya, Malawi, Rwanda and South Africa. Really proud to have 800 AA grads to over 400 bachelor's graduates and nearly 1,000 students enrolled right now.So, the magic of this is that we're addressing refugee lives as they exist. There are no classes. There are no lectures. There are no due dates. There are no final exams. This degree is competency-based and not time-bound. You choose when you start your project. You choose how you're going to approach it.NDD: When you open the platform, that's where you can see the goals. Under each goal, we can find projects. When you open a project, you get the competencies that you have to master, directions and overview of the project.CR: The secret sauce of SNHU is combining that competency-based online learning with the in-person learning that we do with partners to provide all the wraparound supports. That includes academic coaching. It means psychosocial support, medical support, and it's also that back-end employment support that's really resulting in the 95 percent graduation, the 88 percent employment.NDD: I'm a social media management intern. It's related to the communications degree I'm doing. I've learned so many things out of the project and in the real world.CR: The structured internship is really an opportunity for students to practice their skills, for us to create connections between that internship and a later job opportunity.(Music)This is a model that really stops putting time and university policies and procedures at the center and instead puts the student at the center.IM: The SNHU model is a big way to shake the tree. Huge. It's a huge shake to the traditional way of having tertiary education here.BDY: It can transform the lives of students from these vulnerable and refugee communities.NDD: If I get the degree, I can just come back and work everywhere that I want. I can go for a masters confidently in English, which is something that I would not have dreamt of before. And I have the confidence and the skills required to actually go out and just tackle the workplace without having to fear that I can't make it.SAS: I always wanted to work with the community. I want to establish a nonprofit. We advocate for women's education. I want to be someone who is, like, an ambassador and encourage them to learn and tell them it is never too late. It's a dream."""
    raw_text = raw_text[:500]
    original_text = ''.join([c.lower() for c in raw_text if c.isalpha() or c == ' '])
    text = ''.join([c.lower() for c in original_text if c.isalpha()])
    print(text)

    hypothesis_dumb = split_every_five_chars(text)
    print(hypothesis_dumb)
    hypothesis_hmm = ' '.join(list(hmm.cut(text)))
    print(hypothesis_hmm)


    print(jiwer.cer(original_text, text))
    print(jiwer.cer(original_text, hypothesis_dumb))
    print(jiwer.cer(original_text, hypothesis_hmm))