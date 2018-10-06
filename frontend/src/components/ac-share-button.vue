<template>
  <v-flex>
    <v-btn color="primary" @click="showModal = true"><v-icon>share</v-icon> Share!</v-btn>
    <v-dialog v-model="showModal" max-width="500px">
      <v-card>
        <v-card-text>
          <v-flex text-xs-center>
            <v-checkbox
                label="Allow NSFW preview image"
                v-model="nsfwPreview"
                v-if="showNSFWToggle"
            />
            <v-checkbox
              label="Include referral information (includes username in URL)"
              v-model="referral"
              v-if="viewer.username"
            />
          </v-flex>
          <v-flex text-xs-center>
            <v-btn color="red" fab :href="`https://reddit.com/submit?url=${location}&title=${titleText}`" target="_blank">
              <v-icon large>fa-reddit</v-icon>
            </v-btn>
            <v-btn color="blue" fab :href="`https://telegram.me/share/url?url=${location}`" target="_blank">
              <v-icon large>fa-telegram</v-icon>
            </v-btn>
            <v-btn color="blue" fab :href="`https://twitter.com/share?text=${titleText}&url=${location}&hashtags=Artconomy`" target="_blank">
              <v-icon>fa-twitter</v-icon>
            </v-btn>
            <v-btn color="gray" fab :href="`https://www.tumblr.com/share/link?url=${location}&name=${titleText}`" target="_blank">
              <v-icon>fa-tumblr</v-icon>
            </v-btn>
          </v-flex>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-flex>
</template>

<script>
  import Viewer from '../mixins/viewer'

  export default {
    name: 'ac-share-button',
    props: ['title', 'targetRating'],
    mixins: [Viewer],
    data () {
      return {
        showModal: false,
        nsfwPreview: false,
        referral: false,
        encodeURIComponent
      }
    },
    created () {
      if (this.viewer) {
        this.referral = true
      }
    },
    computed: {
      titleText () {
        return encodeURIComponent(this.title)
      },
      itemRating () {
        return this.targetRating || 0
      },
      showNSFWToggle () {
        if (this.itemRating < 3) {
          if (this.itemRating > 0) {
            return true
          }
        }
        return false
      },
      location () {
        let route = {...this.$route}
        let query = {...this.$route.query}
        if (this.nsfwPreview) {
          query.nsfw_preview = true
        } else {
          delete query.nsfw_preview
        }
        if (this.referral) {
          query.referred_by = this.viewer.username
        } else {
          delete query.referred_by
        }
        route.query = query
        return encodeURIComponent(
          window.location.protocol + '//' + window.location.host + this.$router.resolve(route).href
        )
      }
    }
  }
</script>

<style scoped>

</style>