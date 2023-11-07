<template>
  <v-expansion-panels v-model="tab">
    <v-expansion-panel>
      <v-expansion-panel-title>
        <strong>What are the content ratings and what do they mean?</strong>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <v-card>
          <v-card-text>
            <p>
              Artconomy caters to varying tastes and strives to give its customers the best viewing
              experience it can. In order to do so, we have instated a handful of 'rating levels'.
              <router-link
                  :to="{name: 'Options', params: {username: viewer!.username}}"
                  v-if="isRegistered"
              >
                Your rating level can be configured in your settings.
              </router-link>
              <span v-else>
                      Your rating level can be configured in your settings.
                    </span>
            </p>
            <p>The following rating levels exist:</p>
            <ol>
              <li>
                Clean/Safe for Work: Content which can be safely viewed in most workplaces. Pieces with nudity
                or especially suggestive clothing do not belong in this category. Pieces with violence or
                potentially offensive messages do not belong in this category, either.
              </li>
              <li>
                Risque/Mature: This is for content which may contain nudity or risque content which is not suitable
                for work but is not explicitly pornographic belongs here.
                Mild violence also belongs in this category.
              </li>
              <li>
                Adult Content: This is for content which is explicitly pornographic but unlikely to violate the
                sensibilities of most viewers of such content. Moderate violence also belongs in this category.
              </li>
              <li>
                Offensive/Disturbing: This is for content which is extreme in some regard, such as fetish artwork
                that most viewers would find 'squicky' or disturbing or portrayals of extreme violence.
              </li>
            </ol>
            <p>
              <strong>
                If there is any reasonable doubt a piece belongs in one category or the or the next one, place
                it in the next one.
              </strong>
            </p>
            <p>
              Users are expected to categorize their pieces in good faith. If users do not properly categorize,
              pieces may be categorized for them. Repeated failure to properly categorize can
              result in account suspension.
            </p>
            <p>
              If you set a maximum content rating higher than the default of Clean/Safe for work, you will have
              access to the NSFW/SFW toggle button in the menu. Clicking this will quickly make your experience more
              presentable for a work environment.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-text>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-title>
        <strong>What is your content policy?</strong>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <p>
          In general, the policy is 'nothing illegal in the state of Texas, USA.' We don't believe in telling you what
          you can and can't draw. The requirement we have is that content must be properly tagged, especially NSFW
          content. If users cannot
          <router-link :to="{name: 'Other', params: {question: 'tag-blocking'}}">block your content by tag</router-link>
          (and by
          <router-link :to="{name: 'Other', params: {question: 'content-ratings'}}">rating</router-link>
          as applicable) your account may be subject to disciplinary action.
        </p>
        <p>
          There is some content which is legal but which is also not permitted:
        </p>
        <ul>
          <li>Explicit photos of humans</li>
          <li>Photographs of humans uploaded without consent</li>
          <li>Photomanipulations of humans which are explicit</li>
          <li>
            Computer generated explicit content of humans which is indistinguishable (or only distinguishable with
            difficulty) from photographs.
          </li>
          <li>Non-art content-- such as datasets or programs that aren't reasonably understood by our staff to have
            artistic purpose or merit.
          </li>
        </ul>

        Artconomy is hosted in the state of Texas and is subject to the laws of it and the United States of America.
        Some examples of content which is illegal here and not covered in the above prohibitions include:

        <ul>
          <li>Criminal Threats</li>
          <li>Content which violates Intellectual Property laws-- such as content you did not create and don't have
            permission to upload
          </li>
          <li>Incitement to imminent lawless action</li>
        </ul>

        This is not an exhaustive list. If you are unsure if your content is illegal, please consult with your
        attorney. You may also check our
        <router-link :to="{name: 'TermsOfService'}">Terms of Service</router-link>
        for more information. Artconomy staff is not a legal team, but will remove violating content on our best
        judgement.
      </v-expansion-panel-text>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-title>
        <strong>What is your tagging policy?</strong>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <p>Artconomy has
          <router-link :to="{name: 'Other', params: {question: 'content-policy'}}">very few restrictions</router-link>
          on what content may be posted, but with this freedom comes a responsibility to tag content effectively.
          Tagging content serves the following purposes:
        </p>
        <ul>
          <li>It makes products, submissions, and characters easy for visitors to find via search. Customers interested
            in your content may not be able to find it if it is not properly tagged.
          </li>
          <li>It makes such content easy to
            <router-link :to="{name: 'Other', params: {question: 'tag-blocking'}}">block</router-link>
            for
            those who do not wish to see it.
          </li>
        </ul>
        <p>
          In sum, tagging allows viewers of the site to have control over their experience, and tagging allows artists
          to find their audience. This, in combination with
          <router-link :to="{name: 'Other', params: {question: 'content-policy'}}">content ratings</router-link>
          allows Artconomy to serve a wide, often disparate range of content without telling artists what they may or
          may not create.
        </p>
        <p>These purposes guide tagging-- which means that
          <strong>appearances are more important than lore-based truth</strong> for content. This is commonly referred
          to as a <strong>tag what you see</strong> policy. Tag what you see is the first priority, but you may also
          tag for lore accuracy when it's in conflict with what's visible 'in frame' for a piece.</p>
        <p>
          At the time of writing, minimum tag requirements are not technically enforced, but will be eventually.
          However, even with a minimum number of tags, it is not always clear what kind of content warrants tagging,
          or how to go about it. We therefore offer the following guidelines:
        </p>
        <ul>
          <li>
            Always seek to use existing tags rather than creating new ones. If one does not exist for the thing you are
            tagging, only then should you create one.
          </li>
          <li>
            Character species should always be tagged. If a species is not a real-world species, but based on a
            real-world species, it is recommended to at least tag the real-world species, and preferably the name of the
            fantasy species as well. For example, a 'human' tag is best applied to drawings featuring elves, because
            even though elves are not human, they are substantially based upon them. In such cases the 'human' tag
            should be applied, and preferably 'elf' as well.
          </li>
          <li>
            Apparent character sex should always be tagged-- if actual sex is different from apparent sex, that should
            be tagged as well. You are encouraged to tag a character's gender. If a character is sexless and/or
            genderless, you should tag to this effect.
          </li>
          <li>
            Kinks depicted in a piece must be tagged, as should any body parts that are the focus of a piece, or any
            fetish gear/accessories featured in a piece.
          </li>
          <li>
            If a piece is within a specific genre or style, that should be tagged. Examples include 'furry', 'anime',
            'manga', 'cubism', etc.
          </li>
          <li>
            If a piece utilizes a specific technique or discipline, that should be tagged. Examples include
            'lines', 'watercolor', 'traditional', 'digital', 'sketch', 'origami', etc.
          </li>
          <li>
            If an automated tool significantly contributes to the creation of a piece, that tool and its general
            category must be tagged. Examples include 'AI Assisted', 'AI Generated', 'Stable Diffusion', etc.
          </li>
        </ul>
        <p>
          Tagging is an art in and of itself. We have expectation that users provide a best effort at tagging. To help
          keep tag quality high, some pages allow for all users to contribute and modify tags. If you see a submission
          which is not tagged properly, you are encouraged to tag it. If users are tagging your work inappropriately,
          you may disable public tagging in your
          <router-link
              :to="{name: 'Options', params: {username: viewer!.username}}"
              v-if="isRegistered"
          >
            settings
          </router-link>
          <span v-else>settings</span>.
        </p>
        <p>
          Users who repeatedly fail to observe tagging guidelines, especially those who do not tag content that is
          considered extreme or offensive by most viewers, will have their account subject to disciplinary action.
        </p>
      </v-expansion-panel-text>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-title>
        <strong>How do I block tags I don't want to see?</strong>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <v-card>
          <v-card-text>
            <p>
              Artconomy's rating system is good for course grain categorization of content, but the content of any
              given work may be less desirable to a viewer even if it might normally be in a rating they are
              comfortable with.
            </p>
            <p><strong>Enter tag blocking:</strong>
              When you encounter content that is against your tastes, check the tags on the work.
              Once you locate a tag related to the content you find objectionable, you can go to
              <router-link
                  :to="{name: 'Options', params: {username: viewer!.username}}"
                  v-if="isRegistered"
              >
                your settings page
              </router-link>
              <span v-else>
                      your settings page
                    </span>
              and add it to your blocked tags. From then on, content with that tag will be filtered out.
            </p>
            <p>
              Proper tagging is important. Users are expected to tag their artwork and, by default, all pieces can
              have tags added by other users. Users who disable tagging for their pieces are responsible for their
              tags and may be subject to disciplinary action if they do not maintain a reasonable list of tags for
              their pieces, since this may result in disturbing content being shown to users who do not desire it.
            </p>
            <p>
              Artconomy's
              <router-link :to="{name: 'Other', params: {question: 'content-policy'}}">content policy</router-link>
              is very permissive, and does not prevent disturbing or offensive imagery from being uploaded,
              especially since pieces may be marked private. We prefer to give each customer the power to customize his
              or her viewing experience using the rating, user blocking and tag blocking tools.
            </p>
            <p>
              Artconomy does, however, respond to legal requests to remove unlawful content, and does not permit
              unlawful content on its platform.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-text>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-title>
        <strong>How does watching work?</strong>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <v-card>
          <v-card-text>
            <p>
              You can watch artists by going to their profile page and clicking the Watch button on their profile.
              Watching an artist gives you notifications when they've uploaded new content or when they're
              streaming, or release new products, among other things.
            </p>
            <p>
              The 'Who's Open?' link in the menu takes you to a page where you can see all currently open products
              from artists you are watching.
            </p>
            <p>
              You will also receive notifications when your watched artists are open for commissions!
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-text>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-title>
        <strong>How does Blocking work?</strong>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <v-card>
          <v-card-text>
            <p>
              If you find that someone on Artconomy is harassing you or is otherwise not someone whose content you
              wish to see, you may block them by clicking on the 'block' button on their profile page. Blocking does
              not remove all content from a user, since some information may be contextually important
              (such as comments not made directly in response to yours), however it should block most interactions.
            </p>
            <p>
              If you find a bug in the blocking that allows users to continue harassing you, or you have continued
              to be harassed on the platform after asking someone to stop,
              <a href="#" @click.prevent="$store.commit('supportDialog', true)">please contact support</a> with
              the details. Harassment can be subject to disciplinary action, including account closure, depending on
              severity.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-text>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-title>
        <strong>What file formats are supported? What are the limitations?</strong>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <v-card>
          <v-card-text>
            <p>
              We currently support most file formats used for artistic expression, with a few caveats:
            </p>
            <ul>
              <li>We do not (yet) do automated video conversion.
                You should upload in mp4, or else some viewers may not see your work.
              </li>
              <li>Not all file formats will have useful previews. JPG, GIF, BMP, PNG, and others are supported by
                all browsers, but whatever you upload can be downloaded. You're advised to set the preview icon of
                any piece that doesn't have previewing, such as .PSD files.
              </li>
              <li>The file size limit is currently <strong>100MB</strong>.
                We intend to raise this in the future as we scale.
              </li>
              <li>.TXT files will be previewed with Markdown.</li>
              <li>
                If you're using a file type that is not supported, please upload a .zip file. Do note that uploads
                to Artconomy are expected to be artistic expressions and renderings and they may be removed if
                they are found to be primarily data sets (such as database dumps), non-game programs, or other work
                not reasonably understood as art.
              </li>
            </ul>
          </v-card-text>
        </v-card>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer'
import QuestionSet from '@/components/views/faq/mixins/question-set'

@Component({})
class Other extends mixins(Viewer, QuestionSet) {
  public questions = [
    'content-ratings', 'content-policy', 'tagging', 'tag-blocking', 'watching', 'blocking', 'file-formats',
  ]
}

export default toNative(Other)
</script>
