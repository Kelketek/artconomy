<template>
  <v-container fluid class="pa-0 ma-0 comment-list">
    <v-row v-if="commentList.moreAvailable || showHistory" no-gutters>
      <v-col v-if="commentList.moreAvailable">
        <v-btn block variant="flat" @click="commentList.next">
          Load More
          <v-icon right :icon="mdiArrowExpandDown" />
        </v-btn>
      </v-col>
      <v-col v-if="showHistory" class="text-center">
        <v-btn
          class="comment-history-button"
          variant="flat"
          @click="historyToggle = !historyToggle"
        >
          <v-icon v-if="historyToggle" left :icon="mdiEye" />
          <v-icon v-else left :icon="mdiEyeOff" />
          Toggle History
        </v-btn>
      </v-col>
    </v-row>
    <ac-load-section min-height="10rem" :controller="commentList">
      <template #default>
        <template
          v-for="(comment, index) in commentList.list"
          :key="comment.x!.id"
        >
          <ac-comment
            :comment="comment"
            :username="(comment.x!.user && comment.x!.user.username) || ''"
            :comment-list="commentList"
            :nesting="nesting"
            :toplevel="true"
            :locked="locked"
            :alternate="!(index % 2)"
            :show-history="historyToggle"
            :in-history="inHistory"
          />
          <v-divider
            v-if="index + 1 !== commentList.list.length"
            :key="'divider-' + index"
          />
        </template>
      </template>
    </ac-load-section>
    <ac-loading-spinner v-if="commentList.fetching" min-height="10rem" />
    <slot v-if="commentList.ready && !commentList.list.length" name="empty" />
    <ac-new-comment
      v-if="commentList.ready && !locked && !inHistory"
      ref="newComment"
      :comment-list="commentList"
      :alternate="!(commentList.list.length % 2)"
      :guest-ok="guestOk"
      :extra-data="extraData"
    />
    <v-row v-if="locked && commentList.ready && !inHistory" no-gutters>
      <v-col cols="12" class="col-12 text-section text-center">
        Comments have been locked.
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ListController } from "@/store/lists/controller.ts"
import AcLoadingSpinner from "@/components/wrappers/AcLoadingSpinner.vue"
import AcComment from "@/components/comments/AcComment.vue"
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import { QueryParams } from "@/store/helpers/QueryParams.ts"
import { mdiEye, mdiEyeOff, mdiArrowExpandDown } from "@mdi/js"
import { defineAsyncComponent, ref, watch } from "vue"
import { useErrorHandling } from "@/mixins/ErrorHandling.ts"
import type { Comment } from "@/types/main"
import { RawData } from "@/store/forms/types/main"
const AcNewComment = defineAsyncComponent(
  () => import("@/components/comments/AcNewComment.vue"),
)

declare interface AcCommentSectionProps {
  nesting?: boolean
  locked?: boolean
  guestOk?: boolean
  showHistory?: boolean
  inHistory?: boolean
  hardFail?: boolean
  extraData?: RawData
  commentList: ListController<Comment>
}

const props = withDefaults(defineProps<AcCommentSectionProps>(), {
  nesting: false,
  locked: false,
  guestOk: false,
  showHistory: false,
  inHistory: false,
  hardFail: false,
  extraData: () => ({}),
})

const historyToggle = ref(false)

const adjustParams = () => {
  if (historyToggle.value) {
    // eslint-disable-next-line vue/no-mutating-props
    props.commentList.params = {
      ...(props.commentList.params || ({} as QueryParams)),
      ...{ history: "1" },
    }
  } else {
    const params = { ...(props.commentList.params || ({} as QueryParams)) }
    delete params.history
    // eslint-disable-next-line vue/no-mutating-props
    props.commentList.params = params
  }
  if (
    props.commentList.ready ||
    props.commentList.failed ||
    props.commentList.fetching
  ) {
    props.commentList.reset()
  }
}
const { setError } = useErrorHandling()
watch(historyToggle, adjustParams)
adjustParams()
const runPromise = props.commentList.firstRun()
if (props.hardFail) {
  runPromise.catch(setError)
}
if (!props.commentList.reverse) {
  console.error("Comment lists should always be reversed!")
}
</script>
