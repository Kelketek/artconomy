<template>
  <fragment>
    <v-btn color="primary" @click="showModal = true" :block="block">
      <v-icon left>share</v-icon>
      Share
    </v-btn>
    <ac-expanded-property v-model="showModal">
      <v-layout row wrap v-if="social">
        <v-flex text-xs-center xs12>
          <v-checkbox
              label="Include referral information"
              hint=" Includes username in URL, but you get rewards."
              :persistent-hint="true"
              v-model="referral"
              v-if="viewer.username"
              class="referral-check"
          />
        </v-flex>
        <v-flex text-xs-center xs12>
          <v-btn color="red" icon large :href="`https://reddit.com/submit?url=${location}&title=${titleText}`"
                 rel="nofollow"
                 target="_blank">
            <v-icon large>fa-reddit</v-icon>
          </v-btn>
          <v-btn color="blue" icon large :href="`https://telegram.me/share/url?url=${location}`"
                 target="_blank"
                 rel="nofollow"
          >
            <v-icon large>fa-telegram</v-icon>
          </v-btn>
          <v-btn color="blue" icon large
                 :href="`https://twitter.com/share?text=${titleText}&url=${location}&hashtags=Artconomy`"
                 target="_blank"
                 rel="nofollow">
            <v-icon>fa-twitter</v-icon>
          </v-btn>
          <v-btn color="grey darken-4" icon large :href="`https://www.tumblr.com/share/link?url=${location}&name=${titleText}`"
                 target="_blank"
                 rel="nofollow">
            <v-icon>fa-tumblr</v-icon>
          </v-btn>
        </v-flex>
      </v-layout>
      <slot name="footer"></slot>
    </ac-expanded-property>
  </fragment>
</template>

<script lang="ts">
import Viewer from '../mixins/viewer'
import {Fragment} from 'vue-fragment'
import Component, {mixins} from 'vue-class-component'
import Dialog from '../mixins/dialog'
import {Prop} from 'vue-property-decorator'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'

  @Component({components: {AcExpandedProperty, Fragment}})
export default class AcShareButton extends mixins(Dialog, Viewer) {
    @Prop({default: true})
    public social!: boolean
    @Prop({required: true})
    public title!: string
    public showModal = false
    public referral = true
    @Prop()
    public block!: boolean
    public get titleText() {
      return encodeURIComponent(this.title)
    }
    public get location() {
      const route = {...this.$route}
      const query = {...this.$route.query}
      if (this.referral && this.isRegistered) {
        query.referred_by = this.rawViewerName
      } else {
        delete query.referred_by
      }
      route.query = query
      return encodeURIComponent(
        window.location.protocol + '//' + window.location.host + this.$router.resolve(route).href
      )
    }
}
</script>

<style scoped>

</style>
