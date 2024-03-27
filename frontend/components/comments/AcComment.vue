<template>
  <v-card :color="color" :class="{alternate, comment: true, 'elevation-3': alternate, selected}"
          :id="'comment-' + comment.x.id" v-if="comment.x">
    <v-toolbar dense color="black">
      <ac-avatar :username="username" :show-name="false" v-if="username"/>
      <v-toolbar-title v-if="username" class="ml-1">
        <ac-link :to="profileLink(subject)">{{ subjectHandler.displayName }}</ac-link>
      </v-toolbar-title>
      <v-spacer/>
      <v-tooltip bottom>
        <template v-slot:activator="{ props }">
          <v-icon v-bind="props" :icon="mdiInformation"/>
        </template>
        {{ formatDateTime(comment.x.created_on) }}
        <span v-if="comment.x.edited"><br/>Edited: {{ formatDateTime(comment.x.edited_on) }}</span>
      </v-tooltip>
      <v-menu offset-x left v-if="!inHistory" :attach="menuTarget">
        <template v-slot:activator="{props}">
          <v-btn icon v-bind="props" class="more-button" aria-label="Actions">
            <v-icon :icon="mdiDotsHorizontal"/>
          </v-btn>
        </template>
        <v-list dense>
          <v-list-item @click="historyDisplay = true" v-if="showHistory">
            <template v-slot:prepend>
              <v-icon class="history-button" :icon="mdiHistory"/>
            </template>
            <v-list-item-title>Revision history</v-list-item-title>
          </v-list-item>
          <v-list-item @click="editing = true" v-if="!editing && controls">
            <template v-slot:prepend>
              <v-icon class="edit-button" :icon="mdiPencil"/>
            </template>
            <v-list-item-title>Edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click="editing = false" v-if="editing && controls">
            <template v-slot:prepend>
              <v-icon class="lock-button" :icon="mdiCancel"/>
            </template>
            <v-list-item-title>Cancel edit</v-list-item-title>
          </v-list-item>
          <v-list-item @click.stop="comment.patch({subscribed: !comment.x.subscribed})">
            <template v-slot:prepend>
              <v-icon v-if="comment.x.subscribed" :icon="mdiVolumeHigh"/>
              <v-icon v-else :icon="mdiVolumeOff"/>
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
                  <v-icon class="delete-button" :icon="mdiDelete"/>
                </template>
                <v-list-item-title>Delete</v-list-item-title>
              </v-list-item>
            </template>
          </ac-confirmation>
        </v-list>
      </v-menu>
    </v-toolbar>
    <v-card-text ref="main">
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
                          <v-icon :icon="mdiCancel"/>
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
                        <v-icon :icon="mdiReply"/>
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
      <span>BEFORE SECTION!</span>
      <v-row no-gutters v-if="subCommentList.list.length || replying">
        <v-col cols="11" offset="1">
          <v-row no-gutters class="mt-4">
            <v-col v-if="subCommentList.moreAvailable">
              <v-btn block @click="subCommentList.next" variant="flat">
                Load More
                <v-icon right :icon="mdiArrowExpandDown"/>
              </v-btn>
            </v-col>
            <span>THIS WOULD BE HERE!</span>
            <ac-load-section :controller="subCommentList">
              <template v-slot:default>
                <div class="flex subcomments">
                  <template v-for="(comment, index) in subCommentList.list">
                    <ac-comment
                        :alternate="checkAlternate(index)"
                        :comment="comment"
                        :comment-list="subCommentList"
                        :username="comment.x!.user?.username || ''"
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
                    <v-icon :icon="mdiReply"/>
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

<script setup lang="ts">
import {computed, defineAsyncComponent, ref, watch} from 'vue'
import {SingleController} from '@/store/singles/controller.ts'
import {ListController} from '@/store/lists/controller.ts'
import Comment from '@/types/Comment.ts'
import {
  mdiArrowExpandDown,
  mdiDotsHorizontal,
  mdiReply,
  mdiCancel,
  mdiDelete,
  mdiVolumeOff,
  mdiVolumeHigh,
  mdiPencil,
  mdiHistory,
  mdiInformation,
} from '@mdi/js'
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useGoTo, useTheme} from 'vuetify'
import {useViewer} from '@/mixins/viewer.ts'
import {useRoute} from 'vue-router'
import {useList} from '@/store/lists/hooks.ts'
import {useSubject} from '@/mixins/subjective.ts'
import {useTargets} from '@/plugins/targets.ts'
import {formatDateTime, profileLink} from '@/lib/otherFormatters.ts'

const AcAvatar = defineAsyncComponent(() => import('@/components/AcAvatar.vue'))
const AcRendered = defineAsyncComponent(() => import('@/components/wrappers/AcRendered.ts'))
const AcConfirmation = defineAsyncComponent(() => import('@/components/wrappers/AcConfirmation.vue'))
const AcPatchField = defineAsyncComponent(() => import('@/components/fields/AcPatchField.vue'))
const AcExpandedProperty = defineAsyncComponent(() => import('@/components/wrappers/AcExpandedProperty.vue'))
const AcLink = defineAsyncComponent(() => import('@/components/wrappers/AcLink.vue'))
const AcLoadSection = defineAsyncComponent(() => import('@/components/wrappers/AcLoadSection.vue'))
const AcNewComment = defineAsyncComponent(() => import('@/components/comments/AcNewComment.vue'))
const AcCommentSection = defineAsyncComponent(() => import('@/components/comments/AcCommentSection.vue'))

declare interface AcCommentProps {
  comment: SingleController<Comment>,
  commentList: ListController<Comment>,
  alternate?: boolean,
  nesting?: boolean,
  level?: number,
  locked?: boolean,
  showHistory?: boolean,
  inHistory?: boolean,
}

const props = withDefaults(
    defineProps<AcCommentProps & SubjectiveProps>(),
    {
      alternate: false,
      nesting: true,
      level: 0,
      locked: false,
      showHistory: false,
      inHistory: false,
    },
)

const editing = ref(false)
const replying = ref(false)
const scrolled = ref(false)
const historyDisplay = ref(false)
const renderHistory = ref(false)
const main = ref<HTMLElement | null>(null)

const theme = useTheme()
const route = useRoute()
const goTo = useGoTo()

const {isRegistered} = useViewer()
const {
  controls,
  subject,
  subjectHandler,
} = useSubject(props)
const {menuTarget} = useTargets()

const canHaveChildren = computed(() => {
  if (!props.nesting) {
    return false
  }
  return props.level === 0
})

const color = computed(() => {
  if (props.alternate) {
    return theme.current.value.colors['well-darken-4']
  }
  return undefined
})

const canReply = computed(() => {
  return canHaveChildren.value && isRegistered.value && !props.locked
})

const selected = computed(() => {
  if (!props.comment.x) {
    return false
  }
  if (route.query && route.query.commentId) {
    if (route.query.commentId === (props.comment.x!.id + '')) {
      return true
    }
  }
  return false
})

const checkAlternate = (index: number) => {
  if (props.alternate) {
    index += 1
  }
  return !(index % 2)
}

const currentComment = props.comment.x as Comment
const subCommentList = useList<Comment>(props.comment.name.value + '_comments', {
  endpoint: `/api/lib/comments/lib.Comment/${currentComment.id}/`,
  params: {size: 5},
  grow: true,
  reverse: true,
})
const historyList = useList<Comment>(props.comment.name.value + '_history', {
  endpoint: `/api/lib/comments/lib.Comment/${currentComment.id}/history/`,
  params: {size: 5},
  grow: true,
  reverse: true,
})
// Normally we might create a watcher for this param, but the parent list should be refetched if it changes,
// rebuilding the whole comment set.
if (props.showHistory) {
  subCommentList.params = {history: '1'}
}
subCommentList.response = {
  size: 5,
  count: currentComment.comment_count,
}
subCommentList.makeReady(currentComment.comments)

watch(() => subCommentList.list.length, (val: number) => {
  if (props.showHistory || props.inHistory) {
    return
  }
  if (props.comment.x === null) {
    return
  }
  if (val === 0) {
    if (props.comment.x!.deleted) {
      props.comment.setX(null)
    }
  }
})

watch(historyDisplay, (val: boolean) => {
  if (val) {
    renderHistory.value = true
  }
})

watch(main, (el) => {
  if (!el) {
    return
  }
  if (selected.value && !scrolled.value) {
    goTo(el)
    scrolled.value = true
  }
})
</script>
