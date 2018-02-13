<template>
  <div class="comment-block new-comment-component">
    <div v-if="!editing" class="text-xs-center">
      <b-button @click="editing=true" class="new-comment-button">Add a comment</b-button>
    </div>
    <div class="new-comment-block">
      <div v-if="editing && !edit_preview"><textarea :disabled="edit_disabled" v-model="draft"
                                                                        class="comment-field new-comment-field"
                                                                        contenteditable="true"></textarea></div>
      <div v-if="editing && edit_preview" v-html="parseDraft()"></div>
      <div>
        <div class="text-left pull-left preview-button-container" v-if="editing">
          <b-button v-if="edit_preview" variant="info" @click="edit_preview=false"><i class="fa fa-eye"></i></b-button>
          <b-button v-else @click="edit_preview=true"><i class="fa fa-eye"></i></b-button>
          <small class="ml-2">Markdown Syntax Supported</small>
        </div>
        <div v-if="editing" class="text-right comment-actions pull-right">
          <b-button @click="editing=false" variant="danger"><i class="fa fa-times"></i></b-button>
          <b-button @click="save()" variant="success"><i class="fa fa-save"></i></b-button>
        </div>
      </div>
      <div class="clear"></div>
    </div>
  </div>
</template>


<script>
  import { artCall } from '../lib'

  export default {
    name: 'ac-new-comment',
    props: ['parent', 'url'],
    methods: {
      parseDraft () {
        return this.$root.md.render(this.draft)
      },
      addComment (response) {
        this.draft = ''
        this.editing = false
        this.edit_disabled = false
        this.parent.addComment(response)
      },
      save () {
        this.edit_disabled = true
        artCall(
          this.url, 'POST', {'text': this.draft}, this.addComment
        )
      }
    },
    data () {
      return {
        draft: '',
        editing: false,
        edit_preview: false,
        edit_disabled: false
      }
    }
  }
</script>