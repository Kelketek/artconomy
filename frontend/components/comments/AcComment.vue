<template>
  <v-card
    v-if="comment.x"
    :id="'comment-' + comment.x.id"
    :color="color"
    :class="{ alternate, comment: true, 'elevation-3': alternate, selected }"
  >
    <v-toolbar dense color="black">
      <ac-avatar v-if="username" :username="username" :show-name="false" />
      <v-toolbar-title v-if="username" class="ml-1">
        <ac-link :to="profileLink(subject)">
          {{ subjectHandler.displayName }}
        </ac-link>
      </v-toolbar-title>
      <v-spacer />
      <v-tooltip bottom>
        <template #activator="activator">
          <v-icon v-bind="activator.props" :icon="mdiInformation" />
        </template>
        {{ formatDateTime(comment.x.created_on) }}
        <span v-if="comment.x.edited"
          ><br />Edited: {{ formatDateTime(comment.x.edited_on) }}</span
        >
      </v-tooltip>
      <v-menu v-if="!inHistory" offset-x left :attach="menuTarget">
        <template #activator="activator">
          <v-btn
            icon
            v-bind="activator.props"
            class="more-button"
            aria-label="Actions"
          >
            <v-icon :icon="mdiDotsHorizontal" />
          </v-btn>
        </template>
        <v-list dense>
          <v-list-item v-if="showHistory" @click="historyDisplay = true">
            <template #prepend>
              <v-icon class="history-button" :icon="mdiHistory" />
            </template>
            <v-list-item-title>Revision history</v-list-item-title>
          </v-list-item>
          <v-list-item v-if="!editing && controls" @click="editing = true">
            <template #prepend>
              <v-icon class="edit-button" :icon="mdiPencil" />
            </template>
            <v-list-item-title>Edit</v-list-item-title>
          </v-list-item>
          <v-list-item v-if="editing && controls" @click="editing = false">
            <template #prepend>
              <v-icon class="lock-button" :icon="mdiCancel" />
            </template>
            <v-list-item-title>Cancel edit</v-list-item-title>
          </v-list-item>
          <v-list-item
            @click.stop="comment.patch({ subscribed: !comment.x.subscribed })"
          >
            <template #prepend>
              <v-icon v-if="comment.x.subscribed" :icon="mdiVolumeHigh" />
              <v-icon v-else :icon="mdiVolumeOff" />
            </template>
            <v-list-item-title>
              Notifications
              <span v-if="comment.x.subscribed">on</span>
              <span v-else>off</span>
            </v-list-item-title>
          </v-list-item>
          <ac-confirmation v-if="controls" :action="comment.delete">
            <template #default="confirmContext">
              <v-list-item v-on="confirmContext.on">
                <template #prepend>
                  <v-icon class="delete-button" :icon="mdiDelete" />
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
                v-if="controls"
                field-type="ac-editor"
                :auto-grow="editing"
                :patcher="comment.patchers.text"
                :auto-save="false"
              >
                <template #pre-actions>
                  <v-col class="shrink">
                    <v-tooltip top>
                      <template #activator="activator">
                        <v-btn
                          v-bind="activator.props"
                          icon
                          small
                          color="danger"
                          class="cancel-button"
                          :disabled="!!comment.patchers.text.patching"
                          @click="editing = false"
                        >
                          <v-icon :icon="mdiCancel" />
                        </v-btn>
                      </template>
                      <span>Cancel</span>
                    </v-tooltip>
                  </v-col>
                </template>
              </ac-patch-field>
              <ac-rendered
                v-show="!editing"
                v-if="!comment.x.deleted"
                :value="comment.x.text"
              />
              <v-col v-else> [Deleted] </v-col>
            </v-col>
            <v-col
              v-if="
                canReply &&
                !editing &&
                !comment.x.deleted &&
                !subCommentList.list.length &&
                !replying
              "
              class="text-right"
              cols="12"
            >
              <v-row no-gutters>
                <v-spacer />
                <v-col class="shrink">
                  <v-tooltip top>
                    <template #activator="activator">
                      <v-btn
                        v-bind="activator.props"
                        color="primary"
                        icon
                        small
                        class="reply-button"
                        @click="replying = true"
                      >
                        <v-icon :icon="mdiReply" />
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
      <v-row v-if="subCommentList.list.length || replying" no-gutters>
        <v-col cols="11" offset="1">
          <v-row no-gutters class="mt-4">
            <v-col v-if="subCommentList.moreAvailable">
              <v-btn block variant="flat" @click="subCommentList.next">
                Load More
                <v-icon right :icon="mdiArrowExpandDown" />
              </v-btn>
            </v-col>
            <ac-load-section :controller="subCommentList">
              <template #default>
                <div class="flex subcomments">
                  <template v-for="(subComment, index) in subCommentList.list">
                    <ac-comment
                      v-if="subComment.x"
                      :key="subComment.x!.id"
                      :alternate="checkAlternate(index)"
                      :comment="subComment"
                      :comment-list="subCommentList"
                      :username="subComment.x!.user?.username || ''"
                      :level="level + 1"
                      :nesting="nesting"
                      :show-history="showHistory"
                    />
                  </template>
                </div>
              </template>
            </ac-load-section>
            <v-col v-if="replying" cols="12">
              <ac-new-comment
                v-if="replying"
                v-model="replying"
                :comment-list="subCommentList"
                :alternate="checkAlternate(subCommentList.list.length)"
              />
            </v-col>
          </v-row>
        </v-col>
        <v-col
          v-if="subCommentList.list.length && canReply && !replying"
          cols="12"
          class="pt-2"
        >
          <v-row no-gutters>
            <v-spacer />
            <v-col class="shrink">
              <v-tooltip top>
                <template #activator="activator">
                  <v-btn
                    v-bind="activator.props"
                    color="primary"
                    small
                    icon
                    class="reply-button"
                    @click="replying = true"
                  >
                    <v-icon :icon="mdiReply" />
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
      <ac-comment-section
        v-if="renderHistory"
        :locked="true"
        :comment-list="historyList"
        :in-history="true"
        class="comment-history"
      />
    </ac-expanded-property>
  </v-card>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, ref, watch } from "vue"
import { SingleController } from "@/store/singles/controller.ts"
import { ListController } from "@/store/lists/controller.ts"
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
} from "@mdi/js"
import { useGoTo, useTheme } from "vuetify"
import { useViewer } from "@/mixins/viewer.ts"
import { useRoute } from "vue-router"
import { useList } from "@/store/lists/hooks.ts"
import { useSubject } from "@/mixins/subjective.ts"
import { useTargets } from "@/plugins/targets.ts"
import { formatDateTime, profileLink } from "@/lib/otherFormatters.ts"
import type { Comment, SubjectiveProps } from "@/types/main"

const AcAvatar = defineAsyncComponent(() => import("@/components/AcAvatar.vue"))
const AcRendered = defineAsyncComponent(
  () => import("@/components/wrappers/AcRendered.ts"),
)
const AcConfirmation = defineAsyncComponent(
  () => import("@/components/wrappers/AcConfirmation.vue"),
)
const AcPatchField = defineAsyncComponent(
  () => import("@/components/fields/AcPatchField.vue"),
)
const AcExpandedProperty = defineAsyncComponent(
  () => import("@/components/wrappers/AcExpandedProperty.vue"),
)
const AcLink = defineAsyncComponent(
  () => import("@/components/wrappers/AcLink.vue"),
)
const AcLoadSection = defineAsyncComponent(
  () => import("@/components/wrappers/AcLoadSection.vue"),
)
const AcNewComment = defineAsyncComponent(
  () => import("@/components/comments/AcNewComment.vue"),
)
const AcCommentSection = defineAsyncComponent(
  () => import("@/components/comments/AcCommentSection.vue"),
)

declare interface AcCommentProps {
  comment: SingleController<Comment>
  commentList: ListController<Comment>
  alternate?: boolean
  nesting?: boolean
  level?: number
  locked?: boolean
  showHistory?: boolean
  inHistory?: boolean
}

const props = withDefaults(defineProps<AcCommentProps & SubjectiveProps>(), {
  alternate: false,
  nesting: true,
  level: 0,
  locked: false,
  showHistory: false,
  inHistory: false,
})

const editing = ref(false)
const replying = ref(false)
const scrolled = ref(false)
const historyDisplay = ref(false)
const renderHistory = ref(false)
const main = ref<HTMLElement | null>(null)

const theme = useTheme()
const route = useRoute()
const goTo = useGoTo()

const { isRegistered } = useViewer()
const { controls, subject, subjectHandler } = useSubject({
  props,
  controlPowers: ["moderate_discussion"],
})
const { menuTarget } = useTargets()

const canHaveChildren = computed(() => {
  if (!props.nesting) {
    return false
  }
  return props.level === 0
})

const color = computed(() => {
  if (props.alternate) {
    return theme.current.value.colors["well-darken-4"]
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
    if (route.query.commentId === props.comment.x!.id + "") {
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
const subCommentList = useList<Comment>(
  props.comment.name.value + "_comments",
  {
    endpoint: `/api/lib/comments/lib.Comment/${currentComment.id}/`,
    params: { size: 5 },
    grow: true,
    reverse: true,
  },
)
const historyList = useList<Comment>(props.comment.name.value + "_history", {
  endpoint: `/api/lib/comments/lib.Comment/${currentComment.id}/history/`,
  params: { size: 5 },
  grow: true,
  reverse: true,
})
// Normally we might create a watcher for this param, but the parent list should be refetched if it changes,
// rebuilding the whole comment set.
if (props.showHistory) {
  subCommentList.params = { history: "1" }
}
subCommentList.response = {
  size: 5,
  count: currentComment.comment_count,
}
subCommentList.makeReady(currentComment.comments)

watch(
  () => subCommentList.list.length,
  (val: number) => {
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
  },
)

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

<style lang="stylus" scoped>
.comment p:last-child {
  margin-bottom: 0;
}

.comment.selected {
  box-shadow: inset 0 0 10px 0 #fff !important;
}
</style>
