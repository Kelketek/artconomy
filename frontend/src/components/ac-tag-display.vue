<template>
  <div class="tag-display">
    <h3>Tags</h3>
    <ac-tag
        v-for="tag in tagList"
        :tag="tag"
        :key="tag"
        :removable="controls"
        :remove-url="`${url}tag/`"
        :callback="callback"
        :tab-name="tabName"
    />
    <div class="pt-2 pb-2" v-if="editable">
      <b-button v-if="!showTagging" @click="showTagging=true">Add Tags</b-button>
      <div v-else>
        <form>
          <ac-form-container
              ref="taggingForm"
              :url="`${this.url}tag/`"
              :schema="taggingSchema"
              :options="taggingOptions"
              :model="taggingModel"
              :success="postTag"
          />
          <b-button variant="danger" @click.prevent="showTagging=false">Cancel</b-button>
          <b-button class="pulse" type="submit" @click.prevent="$refs.taggingForm.submit">Tag!</b-button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
  import AcTag from './ac-tag'
  import AcFormContainer from './ac-form-container'

  export default {
    props: {
      callback: {},
      editable: false,
      url: {},
      tagList: {},
      controls: {},
      tabName: {
        default: 'submissions'
      }
    },
    data () {
      return {
        taggingSchema: {
          fields: [
            {
              type: 'tag-search',
              model: 'tags',
              label: 'tags',
              featured: true,
              placeholder: 'Search tags',
              styleClasses: 'field-input'
            }
          ]
        },
        taggingModel: {
          tags: []
        },
        taggingOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        },
        showTagging: false
      }
    },
    methods: {
      postTag (response) {
        this.callback(response)
        this.showTagging = false
      }
    },
    components: {
      AcFormContainer,
      AcTag
    },
    name: 'ac-tag-display'
  }
</script>

<style scoped lang="scss">
  @import '../custom-bootstrap';
  .pulse {
    animation: pulse_animation 2s infinite;
  }
  @keyframes pulse_animation {
    0% { background-color: $primary; }
    25% {background-color: lighten($primary, 20)}
    50% { background-color: $secondary; }
    75% {background-color: lighten($secondary, 20)}
    100% { background-color: $primary; }
  }
</style>