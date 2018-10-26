<template>
  <div class="tag-display">
    <h3 v-if="!hideTitle">Tags</h3>
    <ac-tag
        v-for="tag in tagList"
        :tag="tag"
        :key="tag"
        :removable="controls"
        :remove-url="url"
        :callback="callback"
        :tab-name="tabName"
    />
    <div class="pt-2 pb-2" v-if="editable">
      <v-btn v-if="!showTagging && isLoggedIn" @click="showTagging=true">Add Tags</v-btn>
      <div v-else-if="isLoggedIn">
        <form>
          <ac-form-container
              ref="taggingForm"
              :url="url"
              :schema="taggingSchema"
              :options="taggingOptions"
              :model="taggingModel"
              :success="postTag"
          />
          <v-btn color="danger" @click.prevent="showTagging=false">Cancel</v-btn>
          <v-btn class="pulse" type="submit" @click.prevent="$refs.taggingForm.submit">Tag!</v-btn>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
  import AcTag from './ac-tag'
  import AcFormContainer from './ac-form-container'
  import Viewer from '../mixins/viewer'

  export default {
    props: {
      callback: {},
      editable: false,
      url: {},
      tagList: {},
      controls: {},
      tabName: {
        default: 'submissions'
      },
      hideTitle: {
        default: false
      }
    },
    mixins: [Viewer],
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

<style scoped>
  .pulse {
    animation: pulse_animation 2s infinite;
  }
  @keyframes pulse_animation {
    0% { background-color: #5f2480 }
    25% {background-color: #735c94 }
    50% { background-color: #82204A }
    75% {background-color: #96345e}
    100% { background-color: #5f2480 }
  }
</style>