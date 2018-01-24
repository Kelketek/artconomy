<template>
  <router-link :to="{name: 'Submission', params: {'assetID': event.target.id}}">
    <div class="row">
      <div class="col-4 col-lg-2">
        <ac-asset class="p-2" :terse="true" :asset="event.target" thumb-name="notification" />
      </div>
      <div class="col-6">
        <div class="p2">
          <p>
            <strong>
              Tags have been added to your submission<span v-if="event.target.title"> titled '{{event.target.title}}'</span>!
            </strong>
          </p>
          <p v-if="tags.length">
            <ac-tag
                v-for="tag in event.data.tags"
                :tag="{name: tag}"
                :key="tag"
            />
          </p>
          <p v-else>
            The tags appear to have since been removed.
          </p>
        </div>
      </div>
    </div>
  </router-link>
</template>

<style scoped>
  .hidden {
    border-bottom: 0;
  }
</style>

<script>
  import AcAsset from '../ac-asset'
  import AcTag from '../ac-tag'
  export default {
    name: 'ac-submission-tag',
    components: {
      AcTag,
      AcAsset
    },
    props: ['event'],
    data () {
      return {}
    },
    computed: {
      tags () {
        if (!(this.event.data.tags && this.event.data.tags.length)) {
          return []
        }
        if (!this.event.target) {
          return []
        }
        let currentTags = this.event.target.tags.map(x => x.name)
        let shownTags = []
        for (let tag of this.event.data.tags) {
          if (currentTags.indexOf(tag) !== -1) {
            shownTags.push(tag)
          }
        }
        return shownTags
      },
      hidden () {
        return !this.tags.length
      }
    }
  }
</script>