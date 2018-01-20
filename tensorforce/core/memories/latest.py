# Copyright 2017 reinforce.io. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import tensorflow as tf

from tensorforce.core.memories import Queue


class Latest(Queue):

    def __init__(self, states, actions, include_next_states, capacity, scope='latest', summary_labels=None):
        super(Latest, self).__init__(
            states=states,
            actions=actions,
            include_next_states=include_next_states,
            capacity=capacity,
            scope=scope,
            summary_labels=summary_labels
        )

    def tf_retrieve_timesteps(self, n):
        num_timesteps = (self.memory_index - self.episode_indices[0] - 2) % self.capacity + 1
        n = tf.minimum(x=n, y=num_timesteps)
        # n = tf.Print(n, (self.memory_index, self.episode_count, self.episode_indices[:self.episode_count + 1], n), summarize=64)
        indices = tf.range(
            start=(self.memory_index - 1 - n),
            limit=(self.memory_index - 1)
        ) % self.capacity
        terminal = tf.gather(params=self.terminal_memory, indices=indices)
        indices = tf.boolean_mask(tensor=indices, mask=tf.logical_not(x=terminal))
        return self.retrieve_indices(indices=indices)

    def tf_retrieve_episodes(self, n):
        n = tf.minimum(x=n, y=self.episode_count)
        # n = tf.Print(n, (self.memory_index, self.episode_count, self.episode_indices[:self.episode_count + 1], n))
        start = self.episode_indices[self.episode_count - n - 1] + 1
        limit = self.episode_indices[self.episode_count - 1]
        limit += tf.where(condition=(start < limit), x=0, y=self.capacity)
        indices = tf.range(start=start, limit=limit) % self.capacity
        # indices = tf.Print(indices, (tf.shape(indices), start, limit))
        return self.retrieve_indices(indices=indices)

    def tf_retrieve_sequences(self, n, sequence_length):
        num_timesteps = (self.memory_index - self.episode_indices[0] - 2) % self.capacity + 1
        n = tf.minimum(x=n, y=(num_timesteps - sequence_length))
        # n = tf.Print(n, (self.memory_index, self.episode_count, self.episode_indices[:self.episode_count + 1], n), summarize=64)
        indices = tf.range(
            start=(self.memory_index - 1 - n - sequence_length),  # or '- 1' implied in sequence length?
            limit=(self.memory_index - 1)
        ) % self.capacity
        sequence_indices = [indices[k: k + sequence_length] for k in range(n)]
        sequence_indices = tf.stack(values=sequence_indices, axis=0)
        terminal = tf.gather(params=self.terminal_memory, indices=indices)
        sequence_indices = tf.boolean_mask(tensor=sequence_indices, mask=tf.logical_not(x=terminal))
        return self.retrieve_indices(indices=sequence_indices)
