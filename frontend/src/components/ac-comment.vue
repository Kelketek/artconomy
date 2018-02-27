<template>
  <v-card :id="'comment-' + comment.id" class="comment-block"
       :class="{'my-comment': myComment, 'elevation-3': alternate, 'pt-2': true, 'mb-2': true}">
    <v-layout row wrap>
      <v-flex xs12 sm2 class="text-xs-center comment-info pb-2">
        <ac-avatar :user="comment.user" /><br />
        <v-tooltip bottom>
          <span slot="activator" class="underlined" :id="'comment-' + comment.id + '-created_on'">
            commented
            <span :id="'comment-' + comment.id + '-edited_on'" class="underlined" v-if="comment.edited"><small>(edited)</small></span>
          </span>
          {{format_time(comment.created_on)}}
          <span v-if="comment.edited"><br />Edited: {{format_time(comment.edited_on)}}</span>
        </v-tooltip>
      </v-flex>
      <v-flex xs12 md10 class="comment-content pl-2 pr-2" v-html="parseContent()" v-if="!editing && !comment.deleted" />
      <v-flex xs12 md10 class="comment-content pl-2 pr-2" v-if="comment.deleted">[This comment has been deleted]</v-flex>
      <v-flex xs12 md10 v-if="editing && !edit_preview"><textarea :disabled="edit_disabled" v-model="draft"
                                                                        class="comment-field pl-2 pr-2"
                                                                        contenteditable="true"></textarea></v-flex>
      <v-flex xs12 md10 v-if="editing && edit_preview" v-html="parseDraft()" />
      <v-flex xs12 md4 text-xs-right v-if="comment.children.length && editing">
        <div class="preview-block">
          <div class="text-xs-center">
            <v-btn small v-if="edit_preview" variant="info" @click="edit_preview=false"><i class="fa fa-eye"></i></v-btn>
            <v-btn small v-else @click="edit_preview=true"><i class="fa fa-eye"></i></v-btn><br />
            <small class="ml-2">Markdown Syntax Supported</small>
          </div>
        </div>
      </v-flex>
      <v-flex text-xs-right v-if="comment.children.length && !comment.deleted">
        <v-btn small v-if="myComment && !editing" @click="deleteComment()" color="error"><i class="fa fa-trash-o"></i>
        </v-btn>
        <v-btn small v-if="myComment && editing" @click="editing=false" color="error"><i class="fa fa-times"></i>
        </v-btn>
        <v-btn small v-if="myComment && !editing && !locked" @click="editing=true" color="warning"><i class="fa fa-edit"></i>
        </v-btn>
        <v-btn small v-if="editing" @click="save()" color="success"><i class="fa fa-save"></i></v-btn>
      </v-flex>
      <v-flex xs11 offset-xs1>
        <ac-comment
            v-for="comm in comment.children"
            :commentobj="comm"
            :key="comm.id"
            :reader="reader"
            :toplevel="false"
            :parent="comment"
            v-if="comment.children !== []"
            :alternate="!alternate"
            :locked="locked"
        />
      </v-flex>
      <v-flex xs11 offset-xs1 class="pr-1" v-if="replying && !reply_preview"><textarea :disabled="reply_disabled" v-model="reply"
                                                                          class="comment-field"
                                                                          contenteditable="true"></textarea></v-flex>
      <v-flex xs11 offset-xs1 v-if="replying && reply_preview" v-html="parseReply()" />
      <v-flex xs12 md4 text-xs-right v-if="!comment.children.length && editing && !comment.deleted">
        <div class="preview-block">
          <div class="text-xs-center">
            <v-btn small v-if="edit_preview" color="info" @click="edit_preview=false"><i class="fa fa-eye"></i></v-btn>
            <v-btn small v-else @click="edit_preview=true"><i class="fa fa-eye"></i></v-btn><br />
            <small class="ml-2">Markdown Syntax Supported</small>
          </div>
        </div>
      </v-flex>
      <v-flex xs12 md3 text-xs-right v-if="replying && !comment.deleted">
        <div class="preview-block">
          <div class="text-xs-center">
          <v-btn small v-if="reply_preview" color="info" @click="reply_preview=false"><i class="fa fa-eye"></i></v-btn>
          <v-btn small v-else @click="reply_preview=true"><i class="fa fa-eye"></i></v-btn><br />
          <small class="ml-2">Markdown Syntax Supported</small>
          </div>
        </div>
      </v-flex>
      <v-flex class="text-xs-right comment-actions" v-if="!comment.deleted">
        <v-btn small v-if="myComment && !comment.children.length && !editing" @click="deleteComment()" color="error"><i
            class="fa fa-trash-o"></i></v-btn>
        <v-btn small v-if="myComment && !comment.children.length && editing" @click="editing=false" color="error"><i
            class="fa fa-times"></i></v-btn>
        <v-btn small v-if="myComment && !editing && !comment.children.length && !locked" color="warning" @click="editing=true"><i
            class="fa fa-edit"></i></v-btn>
        <v-btn small v-if="editing && !comment.children.length" @click="save()" :disabled="edit_disabled"
                  color="success"><i class="fa fa-save"></i></v-btn>
        <v-btn small v-if="toplevel && nesting && !replying && !locked" @click="replying=true" color="info"><i class="fa fa-reply"></i>
        </v-btn>
        <v-btn small v-if="replying" @click="replying=false" color="danger"><i class="fa fa-times"></i></v-btn>
        <v-btn small v-if="replying" @click="postReply()" :disabled="reply_disabled" color="success"><i
            class="fa fa-save"></i></v-btn>
        <div v-if="editing && reply_preview" v-html="parseReply()"></div>
      </v-flex>
    </v-layout>
  </v-card>
</template>

<style scoped>
  .preview-block {
    display: inline-block;
  }
  .comment-block {
    word-wrap: break-word;
  }
</style>

<script>
  import { artCall, md } from '../lib'
  import moment from 'moment'
  import AcAvatar from './ac-avatar'

  export default {
    components: {AcAvatar},
    name: 'ac-comment',
    props: {
      commentobj: {},
      reader: {},
      nesting: {},
      toplevel: {},
      parent: {},
      locked: {default: false},
      alternate: {'default': false}
    },
    methods: {
      parseContent () {
        return md.render(this.comment.text)
      },
      parseDraft () {
        return md.render(this.draft)
      },
      parseReply () {
        return md.render(this.reply)
      },
      reloadComment (response) {
        this.comment = response
        this.editing = false
        this.edit_preview = false
        this.edit_disabled = false
      },
      save () {
        this.edit_disabled = true
        artCall(
          this.url, 'PATCH', {'text': this.draft}, this.reloadComment
        )
      },
      deleteComment () {
        this.edit_disabled = true
        this.reply_disabled = true
        artCall(
          this.url, 'DELETE', {}, this.markDeleted
        )
      },
      markDeleted () {
        this.editing = false
        this.replying = false
        this.comment.deleted = true
        this.comment.text = ''
      },
      addReply (response) {
        this.comment.children.push(response)
        this.replying = false
        this.reply_disabled = false
      },
      postReply () {
        this.reply_disabled = true
        artCall(
          this.url + 'reply/', 'POST', {'text': this.reply, 'parent': this.comment.id}, this.addReply
        )
      },
      format_time (stamp) {
        return moment(stamp).format('dddd, MMMM Do YYYY, h:mm:ss a')
      }
    },
    data () {
      return {
        editing: false,
        draft: this.commentobj.text,
        edit_preview: false,
        replying: false,
        reply: '',
        reply_preview: false,
        reply_disabled: false,
        edit_disabled: false,
        comment: this.commentobj,
        url: '/api/lib/v1/comment/' + this.commentobj.id + '/'
      }
    },
    computed: {
      myComment () {
        return this.comment.user.username === this.reader.username
      }
    }
  }
</script>