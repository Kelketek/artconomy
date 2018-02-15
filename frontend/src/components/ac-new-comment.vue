<template>
  <div class="comment-block new-comment-component">
    <div v-if="!editing" class="text-xs-center">
      <v-btn @click="editing=true" class="new-comment-button">Add a comment</v-btn>
    </div>
    <div class="new-comment-block">
      <div v-if="editing && !edit_preview"><textarea :disabled="edit_disabled" v-model="draft"
                                                                        class="comment-field new-comment-field"
                                                                        contenteditable="true"></textarea></div>
      <div v-if="editing && edit_preview" v-html="parseDraft()"></div>
      <div>
        <div class="text-left pull-left preview-button-container" v-if="editing">
          <v-btn v-if="edit_preview" color="info" @click="edit_preview=false"><i class="fa fa-eye"></i></v-btn>
          <v-btn v-else @click="edit_preview=true"><i class="fa fa-eye"></i></v-btn>
          <small class="ml-2">Markdown Syntax Supported</small>
        </div>
        <div v-if="editing" class="text-right comment-actions pull-right">
          <v-btn @click="editing=false" color="danger"><i class="fa fa-times"></i></v-btn>
          <v-btn @click="save()" color="success"><i class="fa fa-save"></i></v-btn>
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