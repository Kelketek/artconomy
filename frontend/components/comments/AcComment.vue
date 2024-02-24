<template>
  <v-card :color="color" :class="{alternate, comment: true, 'elevation-3': alternate, selected}"
          :id="'comment-' + comment.x.id" v-if="comment.x">
    <v-toolbar dense color="black">
      <ac-avatar :username="username" :show-name="false" v-if="username"/>
      <v-toolbar-title v-if="username" class="ml-1">
        <ac-link :to="profileLink(subject)">{{subjectHandler.displayName}}</ac-link>
      </v-toolbar-title>
      <v-spacer/>
      <v-tooltip bottom>
        <template v-slot:activator="{ props }">
          <v-icon v-bind="props" icon="mdi-information"/>
        </template>
        {{formatDateTime(comment.x.created_on)}}
        <span v-if="comment.x.edited"><br/>Edited: {{formatDateTime(comment.x.edited_on)}}</span>
      </v-tooltip>
      <v-menu offset-x left v-if="!inHistory" :attach="$menuTarget">
        <template v-slot:activator="{props}">
          <v-btn icon v-bind="props" class="more-button">
            <v-icon icon="mdi-dots-horizontal"/>
          </v-btn>
        </template>
        <v-list dense>
          <v-list-item @click="historyDisplay = true" v-if="showHistory">
            <template v-slot:prepend>
              <v-icon class="history-button" icon="mdi-history"/>
            </template>
            <v-list-item-title>Revision history</v-list-item-title>
          </v-list-item>
          <v-list-item @click="editing = true" v-if="!editing && controls">
            <template v-slot:prepend>
              <v-icon class="edit-button" icon="mdi-pencil"/>
            </template>
            <v-list-item-title>Edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click="editing = false" v-if="editing && controls">
            <template v-slot:prepend>
              <v-icon class="lock-button" icon="mdi-cancel"/>
            </template>
            <v-list-item-title>Cancel edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click.stop="comment.patch({subscribed: !comment.x.subscribed})">
            <template v-slot:prepend>
              <v-icon v-if="comment.x.subscribed" icon="mdi-volume-up"/>
              <v-icon v-else icon="mdi-volume-off"/>
            </template>
            <v-list-item-title>
              Notifications
              <span v-if="comment.x.subscribed">on</span>
              <span v-else>off</span>
            </v-list-item-title>
          </v-list-item>
          <ac-confirmation :action="comment.delete" v-if="controls">
            <template v-slot:default="confirmContext">
              <v-list-item v-on="confirmContext.on">
                <template v-slot:prepend>
                  <v-icon class="delete-button" icon="mdi-delete"/>
                </template>
                <v-list-item-title>Delete</v-list-item-title>
              </v-list-item>
            </template>
          </ac-confirmation>
        </v-list>
      </v-menu>
    </v-toolbar>
    <v-card-text>
      <v-row no-gutters>
        <v-col cols="12" sm="12">
          <v-row no-gutters>
            <v-col cols="12">
              <ac-patch-field
                  v-show="editing"
                  field-type="ac-editor"
                  :auto-grow="editing"
                  :patcher="comment.patchers.text"
                  :auto-save="false"
                  v-if="controls"
              >
                <template v-slot:pre-actions>
                  <v-col class="shrink">
                    <v-tooltip top>
                      <template v-slot:activator="{ props }">
                        <v-btn v-bind="props" @click="editing=false" icon small color="danger" class="cancel-button"
                               :disabled="!!comment.patchers.text.patching">
                          <v-icon icon="mdi-cancel"/>
                        </v-btn>
                      </template>
                      <span>Cancel</span>
                    </v-tooltip>
                  </v-col>
                </template>
              </ac-patch-field>
              <ac-rendered v-show="!editing" :value="comment.x.text" v-if="!comment.x.deleted"/>
              <v-col v-else>[Deleted]</v-col>
            </v-col>
            <v-col class="text-right" cols="12"
                   v-if="canReply && !editing && !comment.x.deleted && !subCommentList.list.length && !replying">
              <v-row no-gutters>
                <v-spacer/>
                <v-col class="shrink">
                  <v-tooltip top>
                    <template v-slot:activator="{ props }">
                      <v-btn v-bind="props" color="primary" icon small @click="replying = true" class="reply-button">
                        <v-icon icon="mdi-reply"/>
                      </v-btn>
                    </template>
                    <span>Reply</span>
                  </v-tooltip>
                </v-col>
                <v-col class="shrink"/>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <v-row no-gutters v-if="subCommentList.list.length || replying">
        <v-col cols="11" offset="1">
          <v-row no-gutters class="mt-4">
            <v-col v-if="subCommentList.moreAvailable">
              <v-btn block @click="subCommentList.next" variant="flat">
                <v-icon left>expand_more</v-icon>
                Load More
                <v-icon right icon="mdi-expand-more"/>
              </v-btn>
            </v-col>
            <ac-load-section :controller="subCommentList">
              <template v-slot:default>
                <div class="flex subcomments">
                  <template v-for="(comment, index) in subCommentList.list">
                    <ac-comment
                        :alternate="checkAlternate(index)"
                        :comment="comment"
                        :comment-list="subCommentList"
                        :username="comment.x!.user?.username"
                        :level="level + 1"
                        :key="comment.x!.id"
                        :nesting="nesting"
                        :show-history="showHistory"
                        v-if="comment.x"
                    />
                  </template>
                </div>
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
            <v-spacer/>
            <v-col class="shrink">
              <v-tooltip top>
                <template v-slot:activator="{ props }">
                  <v-btn v-bind="props" color="primary" small icon @click="replying = true" class="reply-button">
                    <v-icon icon="mdi-reply"/>
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
      <ac-comment-section :locked="true" :comment-list="historyList" v-if="renderHistory" :in-history="true"/>
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

import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import {defineAsyncComponent} from 'vue'
import Subjective from '@/mixins/subjective.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {ListController} from '@/store/lists/controller.ts'
import Comment from '@/types/Comment.ts'
import Formatting from '@/mixins/formatting.ts'
const AcAvatar = defineAsyncComponent(() => import('@/components/AcAvatar.vue'))
const AcRendered = defineAsyncComponent(() => import('@/components/wrappers/AcRendered.ts'))
const AcBoundField = defineAsyncComponent(() => import('@/components/fields/AcBoundField.ts'))
const AcFormContainer = defineAsyncComponent(() => import('@/components/wrappers/AcFormContainer.vue'))
const AcConfirmation = defineAsyncComponent(() => import('@/components/wrappers/AcConfirmation.vue'))
const AcLoadingSpinner = defineAsyncComponent(() => import('@/components/wrappers/AcLoadingSpinner.vue'))
const AcPatchField = defineAsyncComponent(() => import('@/components/fields/AcPatchField.vue'))
const AcExpandedProperty = defineAsyncComponent(() => import('@/components/wrappers/AcExpandedProperty.vue'))
const AcLink = defineAsyncComponent(() => import('@/components/wrappers/AcLink.vue'))
const AcLoadSection = defineAsyncComponent(() => import('@/components/wrappers/AcLoadSection.vue'))
const AcNewComment = defineAsyncComponent(() => import('@/components/comments/AcNewComment.vue'))

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
class AcComment extends mixins(Subjective, Formatting) {
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
  public editing = false
  public replying = false
  public missingOk = true
  public scrolled = false
  public historyDisplay = false
  public renderHistory = false

  public get canHaveChildren() {
    if (!this.nesting) {
      return false
    }
    return this.level === 0
  }

  public get color() {
    if (this.alternate) {
      // @ts-ignore
      return this.$vuetify.theme.current.colors['well-darken-4']
    }
    return undefined
  }

  public get canReply() {
    return this.canHaveChildren && this.isRegistered && !this.locked
  }

  public get selected() {
    if (!this.comment.x) {
      return false
    }
    if (this.$route.query && this.$route.query.commentId) {
      if (this.$route.query.commentId === (this.comment.x as Comment).id + '') {
        return true
      }
    }
    return false
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
    if (this.comment.x === null) {
      return
    }
    if (val === 0) {
      // All children are deleted. Are we?
      if ((this.comment.x as Comment).deleted) {
        // Be gone, if so. We won't be on the server anymore, either!
        this.comment.setX(null)
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
        this.$el.scrollIntoView()
        this.scrolled = true
      }
    })
  }

  public created() {
    const comment = this.comment.x as Comment
    this.subCommentList = this.$getList(this.comment.name + '_comments', {
      endpoint: `/api/lib/comments/lib.Comment/${comment.id}/`,
      params: {size: 5},
      grow: true,
      reverse: true,
    })
    this.historyList = this.$getList(this.comment.name + '_history', {
      endpoint: `/api/lib/comments/lib.Comment/${comment.id}/history/`,
      params: {size: 5},
      grow: true,
      reverse: true,
    })
    // Normally we might create a watcher for this param, but the parent list should be refetched if it changes,
    // rebuilding the whole comment set.
    if (this.showHistory) {
      this.subCommentList.params = {history: '1'}
    }
    this.subCommentList.setList(comment.comments)
    this.subCommentList.response = {
      size: 5,
      count: comment.comment_count,
    }
    this.subCommentList.ready = true
    // @ts-ignore
    window.comment = this
  }
}

export default toNative(AcComment)
</script>
