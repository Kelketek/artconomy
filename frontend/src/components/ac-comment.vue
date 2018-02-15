<template>
  <div :id="'comment-' + comment.id" class="comment-block"
       :class="{'my-comment': myComment, 'alternate': alternate}">
    <div class="text-xs-center comment-info">
      <ac-avatar :user="comment.user"></ac-avatar><br />
      <span class="underlined" :id="'comment-' + comment.id + '-created_on'">commented</span>
      <span :id="'comment-' + comment.id + '-edited_on'" class="underlined" v-if="comment.edited"><small><br />(edited)</small></span>
    </div>
    <b-popover :target="'comment-' + comment.id + '-created_on'"
               triggers="hover focus"
               placement="top"
               :content="format_time(comment.created_on)">
    </b-popover>
    <b-popover :target="'comment-' + comment.id + '-edited_on'"
               triggers="hover focus"
               placement="top"
               :content="format_time(comment.edited_on)"
               v-if="comment.edited">
    </b-popover>
    <div class="comment-content" v-html="parseContent()" v-if="!editing && !comment.deleted"></div>
    <div class="comment-content" v-if="comment.deleted">[This comment has been deleted]</div>
    <div v-if="editing && !edit_preview"><textarea :disabled="edit_disabled" v-model="draft"
                                                                      class="comment-field"
                                                                      contenteditable="true"></textarea></div>
    <div v-if="editing && edit_preview" v-html="parseDraft()"></div>
    <div>
      <div class="text-right pull-right comment-actions" v-if="comment.children.length && !comment.deleted">
        <v-btn v-if="myComment && !editing" @click="deleteComment()" color="error"><i class="fa fa-trash-o"></i>
        </v-btn>
        <v-btn v-if="myComment && editing" @click="editing=false" color="error"><i class="fa fa-times"></i>
        </v-btn>
        <v-btn v-if="myComment && !editing && !locked" @click="editing=true" color="warning"><i class="fa fa-edit"></i>
        </v-btn>
        <v-btn v-if="editing" @click="save()" color="success"><i class="fa fa-save"></i></v-btn>
      </div>
      <div class="text-left pull-left preview-button-container" v-if="comment.children.length && editing">
        <v-btn v-if="edit_preview" variant="info" @click="edit_preview=false"><i class="fa fa-eye"></i></v-btn>
        <v-btn v-else @click="edit_preview=true"><i class="fa fa-eye"></i></v-btn>
        <small class="ml-2">Markdown Syntax Supported</small>
      </div>
    </div>
    <div class="clear"></div>
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
    ></ac-comment>
    <div class="card-block" v-if="replying && !reply_preview"><textarea :disabled="reply_disabled" v-model="reply"
                                                                        class="comment-field"
                                                                        contenteditable="true"></textarea></div>
    <div v-if="replying && reply_preview" v-html="parseReply()"></div>
    <div v-if="!comment.deleted">
      <div class="text-left pull-left preview-button-container" v-if="!comment.children.length && editing">
        <v-btn v-if="edit_preview" color="info" @click="edit_preview=false"><i class="fa fa-eye"></i></v-btn>
        <v-btn v-else @click="edit_preview=true"><i class="fa fa-eye"></i></v-btn>
        <small class="ml-2">Markdown Syntax Supported</small>
      </div>
      <div class="text-left pull-left preview-button-container" v-if="replying">
        <v-btn v-if="reply_preview" color="info" @click="reply_preview=false"><i class="fa fa-eye"></i></v-btn>
        <v-btn v-else @click="reply_preview=true"><i class="fa fa-eye"></i></v-btn>
        <small class="ml-2">Markdown Syntax Supported</small>
      </div>
      <div class="text-right comment-actions pull-right">
        <v-btn v-if="myComment && !comment.children.length && !editing" @click="deleteComment()" color="error"><i
            class="fa fa-trash-o"></i></v-btn>
        <v-btn v-if="myComment && !comment.children.length && editing" @click="editing=false" color="error"><i
            class="fa fa-times"></i></v-btn>
        <v-btn v-if="myComment && !editing && !comment.children.length && !locked" color="warning" @click="editing=true"><i
            class="fa fa-edit"></i></v-btn>
        <v-btn v-if="editing && !comment.children.length" @click="save()" :disabled="edit_disabled"
                  color="success"><i class="fa fa-save"></i></v-btn>
        <v-btn v-if="toplevel && nesting && !replying && !locked" @click="replying=true" color="info"><i class="fa fa-reply"></i>
        </v-btn>
        <v-btn v-if="replying" @click="replying=false" color="danger"><i class="fa fa-times"></i></v-btn>
        <v-btn v-if="replying" @click="postReply()" :disabled="reply_disabled" color="success"><i
            class="fa fa-save"></i></v-btn>
        <div v-if="editing && reply_preview" v-html="parseReply()"></div>
      </div>
    </div>
    <div class="clear"></div>
  </div>
</template>

<style>
  .comment-info, .comment-content {
    display: inline-block;
    line-height: 1rem;
  }
  .comment-content {
    margin-left: 1rem;
    vertical-align: middle;
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