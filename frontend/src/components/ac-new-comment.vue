<template>
  <v-card class="comment-block new-comment-component pt-2">
    <v-layout row wrap>
      <v-flex xs12 text-xs-center v-if="!editing">
        <v-btn @click="editing=true" class="new-comment-button">Add a comment</v-btn>
      </v-flex>
      <v-flex xs12 class="pl-2 pr-2" v-if="editing && !edit_preview">
        <textarea
            :disabled="edit_disabled"
            v-model="draft"
            class="comment-field new-comment-field"
            contenteditable="true"
        ></textarea>
      </v-flex>
      <v-flex xs12 v-if="edit_preview" class="pl-2 pr-2" v-html="parseDraft()" />
      <v-flex xs12 md4 text-xs-right v-if="editing">
        <div class="preview-block">
          <div class="text-xs-center">
          <v-btn small v-if="edit_preview" color="info" @click="edit_preview=false"><v-icon>visibility</v-icon></v-btn>
          <v-btn small v-else @click="edit_preview=true"><v-icon>visibility</v-icon></v-btn><br />
          <small class="ml-2">Markdown Syntax Supported</small>
          </div>
        </div>
      </v-flex>
      <v-flex v-if="editing" text-xs-right>
        <v-btn small @click="editing=false" color="danger"><v-icon>close</v-icon></v-btn>
        <v-btn small @click="save()" color="success" class="comment-save"><v-icon>save</v-icon></v-btn>
      </v-flex>
    </v-layout>
  </v-card>
</template>

<style>
  .comment-field {
    width: 100%;
    border: 1px solid grey;
  }
  .preview-block {
    display: inline-block;
  }
  .comment-block {
    word-wrap: break-word;
  }
</style>

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