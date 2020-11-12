<template>
  <v-card :color="color" :class="{alternate, comment: true, 'elevation-3': alternate, selected}" :id="'comment-' + comment.x.id" v-if="comment.x">
    <v-toolbar dense color="black">
      <ac-avatar :username="username" :show-name="false" v-if="username" />
      <v-toolbar-title v-if="username" class="ml-1"><ac-link :to="profileLink(subject)">{{subjectHandler.displayName}}</ac-link></v-toolbar-title><v-spacer />
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-icon v-on="on">info</v-icon>
        </template>
        {{formatDateTime(comment.x.created_on)}}
        <span v-if="comment.x.edited"><br/>Edited: {{formatDateTime(comment.x.edited_on)}}</span>
      </v-tooltip>
      <v-menu offset-x left v-if="!inHistory">
        <template v-slot:activator="{on}">
          <v-btn icon v-on="on" class="more-button"><v-icon>more_horiz</v-icon></v-btn>
        </template>
        <v-list dense>
          <v-list-item @click="historyDisplay = true" v-if="showHistory">
            <v-list-item-action class="history-button"><v-icon>history</v-icon></v-list-item-action>
            <v-list-item-title>Revision history</v-list-item-title>
          </v-list-item>
          <v-list-item @click="editing = true" v-if="!editing && controls">
            <v-list-item-action class="edit-button"><v-icon>edit</v-icon></v-list-item-action>
            <v-list-item-title>Edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click="editing = false" v-if="editing && controls">
            <v-list-item-action class="lock-button"><v-icon>cancel</v-icon></v-list-item-action>
            <v-list-item-title>Cancel edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click.stop="comment.patch({subscribed: !comment.x.subscribed})">
            <v-list-item-action>
              <v-icon v-if="comment.x.subscribed">volume_up</v-icon>
              <v-icon v-else>volume_off</v-icon>
            </v-list-item-action>
            <v-list-item-title>
              Notifications
              <span v-if="comment.x.subscribed">on</span>
              <span v-else>off</span>
            </v-list-item-title>
          </v-list-item>
          <ac-confirmation :action="comment.delete" v-if="controls">
            <template v-slot:default="confirmContext">
              <v-list-item v-on="confirmContext.on">
                <v-list-item-action class="delete-button"><v-icon>delete</v-icon></v-list-item-action>
                <v-list-item-title>Delete</v-list-item-title>
              </v-list-item>
            </template>
          </ac-confirmation>
        </v-list>
      </v-menu>
    </v-toolbar>
    <v-card-text>
      <v-row no-gutters  >
        <v-col cols="12" sm="12">
          <v-row no-gutters  >
            <v-col cols="12">
              <ac-patch-field
                  v-show="editing"
                  field-type="ac-editor"
                  :patcher="commentText"
                  :auto-save="false"
                  v-if="controls"
              >
                <v-col class="shrink" slot="pre-actions">
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-btn v-on="on" @click="editing=false" fab small color="danger" class="cancel-button" :disabled="commentText.patching">
                        <v-icon>cancel</v-icon>
                      </v-btn>
                    </template>
                    <span>Cancel</span>
                  </v-tooltip>
                </v-col>
              </ac-patch-field>
              <ac-rendered v-show="!editing" :value="comment.x.text" v-if="!comment.x.deleted" />
              <v-col v-else>[Deleted]</v-col>
            </v-col>
            <v-col class="text-right" cols="12" v-if="canReply && !editing && !comment.x.deleted && !subCommentList.list.length && !replying">
              <v-row no-gutters>
                <v-spacer />
                <v-col class="shrink">
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-btn v-on="on" color="primary" fab small @click="replying = true" class="reply-button">
                        <v-icon>reply</v-icon>
                      </v-btn>
                    </template>
                    <span>Reply</span>
                  </v-tooltip>
                </v-col>
                <v-col class="shrink" />
              </v-row>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters   v-if="subCommentList.list.length || replying">
        <v-col cols="11" offset="1">
          <v-row no-gutters class="mt-4">
            <v-col v-if="subCommentList.moreAvailable">
              <v-btn block @click="subCommentList.next">
                <v-icon left>expand_more</v-icon>Load More<v-icon right>expand_more</v-icon>
              </v-btn>
            </v-col>
            <ac-load-section :controller="subCommentList">
              <template v-slot:default>
                <div class="flex subcomments">
                  <ac-comment
                    :alternate="checkAlternate(index)"
                    v-for="(comment, index) in subCommentList.list"
                    :comment="comment"
                    :comment-list="subCommentList"
                    :username="comment.x.user.username"
                    :level="level + 1"
                    :key="comment.x.id"
                    :nesting="nesting"
                    :show-history="showHistory"
                  />
                </div >
              </template>
            </ac-load-section>
            <v-col cols="12" v-if="replying">
              <ac-new-comment
                  :commentList="subCommentList"
                  v-if="replying"
                  :alternate="checkAlternate(subCommentList.list.length)"
                  v-model="replying"
              />
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="12" v-if="subCommentList.list.length && canReply && !replying" class="pt-2">
          <v-row no-gutters>
            <v-spacer />
            <v-col class="shrink" >
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn v-on="on" color="primary" small fab @click="replying = true" class="reply-button">
                    <v-icon>reply</v-icon>
                  </v-btn>
                </template>
                <span>Reply</span>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-card-text>
    <ac-expanded-property v-model="historyDisplay">
      <ac-comment-section :locked="true" :comment-list="historyList" v-if="renderHistory" :in-history="true" />
    </ac-expanded-property>
  </v-card>
</template>

<style lang="stylus" scoped>
  .comment p:last-child {
    margin-bottom: 0;
  }
  .comment.selected {
    box-shadow: inset 0 0 10px 0 #fff !important;
  }
</style>

<script lang="ts">

import Component, {mixins} from 'vue-class-component'
import Subjective from '../../mixins/subjective'
import {SingleController} from '@/store/singles/controller'
import {ListController} from '@/store/lists/controller'
import {Prop, Watch} from 'vue-property-decorator'
import AcAvatar from '@/components/AcAvatar.vue'
import AcRendered from '@/components/wrappers/AcRendered'
import AcBoundField from '@/components/fields/AcBoundField'
import Comment from '@/types/Comment'
import {flatten} from '@/lib/lib'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcNewComment from '@/components/comments/AcNewComment.vue'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {Patch} from '@/store/singles/patcher'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

@Component({
  components: {
    AcLoadSection,
    AcLink,
    AcExpandedProperty,
    AcPatchField,
    AcLoadingSpinner,
    AcNewComment,
    AcConfirmation,
    AcFormContainer,
    AcBoundField,
    AcRendered,
    AcAvatar,
  },
})
export default class AcComment extends mixins(Subjective, Formatting) {
    @Prop({required: true})
    public comment!: SingleController<Comment>

    @Prop({required: true})
    public commentList!: ListController<Comment>

    // Used to make sure every other comment is a different style.
    @Prop({default: false})
    public alternate!: boolean

    // When true, allows replies.
    @Prop({default: true})
    public nesting!: boolean

    // When greater than zero, we won't allow direct replies. They must be at the thread level.
    @Prop({default: 0})
    public level!: number

    @Prop({default: false})
    public locked!: boolean

    @Prop({default: false})
    public showHistory!: boolean

    @Prop({default: false})
    public inHistory!: boolean

    public subCommentList: ListController<Comment> = null as unknown as ListController<Comment>
    public historyList: ListController<Comment> = null as unknown as ListController<Comment>
    public commentText: Patch = null as unknown as Patch
    public editing = false
    public replying = false
    public missingOk = true
    public scrolled = false
    public historyDisplay = false
    public renderHistory = false

    public beforeCreate() {
      // Avoid circular definition loop.
      // @ts-ignore
      this.$options.components.AcCommentSection = require('@/components/comments/AcCommentSection.vue').default
      // @ts-ignore
      this.$options.components.AcComment = AcComment
    }

    public get canHaveChildren() {
      if (!this.nesting) {
        return false
      }
      return this.level === 0
    }

    public get color() {
      if (this.alternate) {
        // @ts-ignore
        return this.$vuetify.theme.currentTheme.darkBase.darken4
      }
    }

    public get canReply() {
      return this.canHaveChildren && this.isRegistered && !this.locked
    }

    public get selected() {
      if (this.$route.query && this.$route.query.commentId) {
        if (this.$route.query.commentId === (this.comment.x as Comment).id + '') {
          return true
        }
      }
    }

    public checkAlternate(index: number) {
      if (this.alternate) {
        index += 1
      }
      return !(index % 2)
    }

    @Watch('subCommentList.list.length')
    public syncDeletion(val: number) {
      if (this.showHistory || this.inHistory) {
        return
      }
      if (val === 0) {
        // All children are deleted. Are we?
        if ((this.comment.x as Comment).deleted) {
          // Be gone, if so. We won't be on the server anymore, either!
          this.comment.setX(false)
        }
      }
    }

    @Watch('historyDisplay')
    public historyRender(val: boolean) {
      /* istanbul ignore else */
      if (val) {
        this.renderHistory = true
      }
    }

    public mounted() {
      this.$nextTick(() => {
        if (this.selected && !this.scrolled) {
          this.$goTo('#comment-' + (this.comment.x as Comment).id)
          this.scrolled = true
        }
      })
    }

    public created() {
      const comment = this.comment.x as Comment
      if (this.controls) {
        this.commentText = this.$makePatcher(
          {modelProp: 'comment', attrName: 'text', debounceRate: 300, refresh: false},
        )
      }
      this.subCommentList = this.$getList(this.comment.name + '_comments', {
        endpoint: `/api/lib/v1/comments/lib.Comment/${comment.id}/`,
        pageSize: 5,
        grow: true,
        reverse: true,
      })
      this.historyList = this.$getList(this.comment.name + '_history', {
        endpoint: `/api/lib/v1/comments/lib.Comment/${comment.id}/history/`,
        pageSize: 5,
        grow: true,
        reverse: true,
      })
      // Normally we might create a watcher for this param, but the parent list should be refetched if it changes,
      // rebuilding the whole comment set.
      if (this.showHistory) {
        this.subCommentList.params = {history: '1'}
      }
      this.subCommentList.setList(comment.comments)
      this.subCommentList.response = {size: 5, count: comment.comment_count}
      this.subCommentList.ready = true
      // @ts-ignore
      window.comment = this
    }
}
</script>
