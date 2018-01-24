<template>
  <div class="tag-display">
    <h3>Tags</h3>
    <ac-tag
        v-for="tag in tagList"
        :tag="tag"
        :key="tag.name"
        :removable="controls"
        :remove-url="`${url}tag/`"
        :callback="callback"
        tab-name="submissions"
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
          <b-button type="submit" @click.prevent="$refs.taggingForm.submit">Tag!</b-button>
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
      controls: {}
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

<style scoped>

</style>