<template>
  <v-expansion-panel v-model="tab">
    <v-expansion-panel-content>
      <div slot="header"><strong>What is Artconomy?</strong></div>
      <v-card>
        <v-card-text>
          <p>
            Artconomy is your online marketplace for custom art, especially art of your characters!
            We provide a safe platform for artists and commissioners to work with each other without the
            frustration
            of ad-hoc solutions to tracking outstanding work, finding available artists, and character
            profiles.
          </p>
          <p>
            Artconomy provides many features such as:
          </p>
          <ul>
            <li>Character Profiles</li>
            <li>Stores for artists to sell commissions</li>
            <li>Workload management through
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'awoo-workload-management'}}">
                AWOO
              </router-link>
            </li>
            <li>
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield's
              </router-link>
              escrow for commissions-- artists don't get paid unless the work is complete, and commissioners
              cannot back out once they've sent payment.
            </li>
            <li>Contract agreements for both parties to refer to in case disagreements arise</li>
            <li>
              <router-link
                  :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
              >
                Artconomy Shield's dispute resolution
              </router-link>
              services between artists and commissioners
            </li>
            <li>...And more!</li>
          </ul>
        </v-card-text>
      </v-card>
    </v-expansion-panel-content>
    <v-expansion-panel-content>
      <div slot="header"><strong>Does Artconomy cost money to use?</strong></div>
      <v-card>
        <v-card-text>
          <p>Artconomy is <strong>FREE</strong> to use. Your character gallery is <strong>FREE</strong>, running a
            shop as an artist is <strong>FREE</strong>.</p>

          <p>Artconomy only collects fees for premium services and from orders using
            <router-link
                :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
            >
              Artconomy Shield.
            </router-link>
          </p>

          <p>Sales without
            <router-link
                :to="{name: 'BuyAndSell', params: {question: 'shield'}}"
            >
              Artconomy Shield
            </router-link>
            may be supported by ad revenue or by other means to be determined.
          </p>

          <p>Our money is made in helping commissioners and artists connect. This gives us an incentive to
            help both groups achieve their goals.</p>
        </v-card-text>
      </v-card>
    </v-expansion-panel-content>
    <v-expansion-panel-content>
      <div slot="header"><strong>Who runs Artconomy?</strong></div>
      <v-card>
        <v-card-text>
          <p>Our team consists of people who are passionate about art.</p>
          <v-img src="/static/images/Amber-And-Fox.jpg" :contain="true" max-height="40vh"></v-img>
          <h3>CEO and Lead Developer: Fox Danger Piacenti</h3>
          <p>Fox is a long term online role player who has had a passion to see characters
            come alive online. He has worked as a lead developer, administrator, and director in the recreational
            and professional spheres.</p>
          <p>Fox began work on Artconomy upon observing the difficulties encountered when commissioning, and
            realizing that he rarely commissioned online but frequently did at creative conventions,
            where one could meet face-to-face with artists. He wanted to create a service where it was as easy
            to commission online as it is in person.</p>
          <p>And, yes, that is his legal name.</p>
          <h3>President: Amber R. Criswell</h3>
          <p>Amber is a supporter of all things artistic and exploratory. A writer and musician,
            she makes up for her lack of drawing talent by buying ALL the art and filling her home with it.</p>
          <p>A friend of hers who has supported himself with his art for over 30 years took her on a personalized
            tour of the best artists in her city, telling her when and what to buy – as well as who would and
            would
            not succeed. Asking how he knew that, he told her that art is 80% business and 20% creation, and when
            an artist isn’t treating their work like the business it is, they won’t be in the game much
            longer.</p>

          <p>She believes the marvelous thing about Artconomy is that it honors its users by creating a
            platform that helps with the business side of art so that everyone has time to focus on what they
            actually want – the art!</p>

          <p>Formerly in education and now in neuroscience research, her interests range from post-WWII
            "lost generation" literature to synesthesia and neuropsychology to astrophysics. An avid traveler,
            her favorite city is Paris and her favorite museum is Museu de l'Erotica in Barcelona
            (where she discovered her fascination with 18th century French erotic art). When she's not working,
            she’s catching up on sleep. When she’s not catching up on sleep, she's being entertained by this
            handsome fox that burrowed his way into her life...</p>
        </v-card-text>
      </v-card>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {paramHandleArray} from '@/lib'
import QuestionSet from '@/components/views/faq/mixins/question-set'

const about = ['what-is-artconomy', 'cost', 'team']
  @Component
export default class About extends mixins(Viewer, QuestionSet) {
    @paramHandleArray('question', about)
    public tab!: number
}
</script>