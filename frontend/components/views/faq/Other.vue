<template>
  <v-expansion-panels v-model="tab">
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>What are the content ratings and what do they mean?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              Artconomy caters to varying tastes and strives to give its customers the best viewing
              experience it can. In order to do so, we have instated a handful of 'rating levels'.
              <router-link
                  :to="{name: 'Settings', params: {username: viewer.username, tabName: 'options'}}"
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
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>How do I use the Blacklist?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <v-card>
          <v-card-text>
            <p>
              Artconomy's rating system is good for course grain categorization of content, but the content of any
              given work may be less desirable to a viewer even if it might normally be in a rating they are
              comfortable with.
            </p>
            <p><strong>Enter the Blacklist:</strong>
              When you encounter content that is against your tastes, check the tags on the work.
              Once you locate a tag related to the content you find objectionable, you can go to
              <router-link
                  :to="{name: 'Settings', params: {username: viewer.username, tabName: 'options'}}"
                  v-if="isRegistered"
              >
                your settings page
              </router-link>
              <span v-else>
                      your settings page
                    </span>
              and add it to your blacklist. From then on, content with that tag will be filtered out.
            </p>
            <p>
              Proper tagging is important. Users are expected to tag their artwork and, by default, all pieces can
              have tags added by other users. Users who disable tagging for their pieces are responsible for their
              tags and may be subject to disciplinary action if they do not maintain a reasonable list of tags for
              their pieces, since this may result in disturbing content being shown to users who do not desire it.
            </p>
            <p>
              Artconomy does not actively police content on the platform, and cannot prevent all disturbing or
              offensive imagery from being uploaded, especially since pieces may be marked private. We prefer to
              give each customer the power to customize his or her viewing experience using the rating and blacklist
              tools.
            </p>
            <p>
              Artconomy does, however, respond to legal requests to remove unlawful content, and does not permit
              unlawful content on its platforms.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>How does watching work?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
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
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>How does Blocking work?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
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
              <a href="#" @click.prevent="setSupport(true)">please contact support</a> with
              the details. Harassment can be subject to disciplinary action, including account closure, depending on
              severity.
            </p>
          </v-card-text>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel>
      <v-expansion-panel-header>
        <strong>What file formats are supported? What are the limitations?</strong>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
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
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {paramHandleArray} from '@/lib/lib'
import QuestionSet from '@/components/views/faq/mixins/question-set'

const other = [
  'content-ratings', 'blacklist', 'watching', 'blocking', 'file-formats',
]
  @Component
export default class Other extends mixins(Viewer, QuestionSet) {
    @paramHandleArray('question', other)
    public tab!: number
}
</script>
